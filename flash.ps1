param(
    [Parameter(Mandatory = $true)]
    [string]$Port,

    [string]$Board = "esp32.json"
)

$ErrorActionPreference = "Stop"

# ============================================================
# CONFIG
# ============================================================

$SRCS = @(
    "hw",
    "hw/$([System.IO.Path]::GetFileNameWithoutExtension($Board))",
    "net",
    "uclient",
    "."
)

$HTMLS = @("static")

# ============================================================
# CHECK TOOLS
# ============================================================

if (!(Get-Command ampy -ErrorAction SilentlyContinue)) {
    Write-Error "ampy not found. Install with: pip install adafruit-ampy"
    exit 1
}

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python not found"
    exit 1
}

if (!(Get-Command minify -ErrorAction SilentlyContinue)) {
    Write-Warning "minify not found. Static files will NOT be minified."
    $USE_MINIFY = $false
}
else {
    $USE_MINIFY = $true
}

# ============================================================
# CHECK FILES
# ============================================================

if (!(Test-Path $Board)) {
    Write-Error "Board file not found: $Board"
    exit 1
}

if (!(Test-Path "tools/json2py.py")) {
    Write-Error "tools/json2py.py not found"
    exit 1
}

# ============================================================
# CHECK MPY-CROSS
# ============================================================

$USE_MPY = $false

try {

    python -m mpy_cross --help *> $null

    if ($LASTEXITCODE -eq 0) {

        $USE_MPY = $true

        Write-Host "Using python -m mpy_cross"
    }
}
catch {

    $USE_MPY = $false
}

if (-not $USE_MPY) {

    Write-Warning "mpy_cross not found. Uploading plain .py files."
    Write-Warning "Install with: pip install mpy-cross"
}

# ============================================================
# INIT src\static
# ============================================================


if (!(Test-Path "src\static")) {
    New-Item -ItemType Directory -Path "src\static" | Out-Null
}

# ============================================================
# INIT SUBMODULES
# ============================================================

Write-Host "Initializing git submodules..."

git submodule init
git submodule sync

# ============================================================
# GENERATE BSP
# ============================================================

Write-Host "Generate BSP"

if (Test-Path "src/board.py") {
    Remove-Item "src/board.py" -Force
}

try {

    $json = Get-Content $Board -Raw | ConvertFrom-Json

    $json |
        ConvertTo-Json -Depth 100 |
        python tools/json2py.py |
        Out-File "src/board.py" -Encoding ascii
}
catch {

    Write-Error "Invalid JSON: $Board"
    exit 1
}

$arch = [System.IO.Path]::GetFileNameWithoutExtension($Board)

"ARCH = `"$arch`"" |
    Out-File "src/hw/arch.py" -Encoding ascii

# ============================================================
# HELPERS
# ============================================================

function Invoke-Ampy {

    param(
        [string]$Command,
        [switch]$IgnoreErrors
    )

    Write-Host "ampy $Command"

    try {

        $output = Invoke-Expression "ampy --delay 1 -p $Port $Command 2>&1"

        if ($output) {

            $output | ForEach-Object {
                Write-Host $_
            }
        }

        return $LASTEXITCODE
    }
    catch {

        if (-not $IgnoreErrors) {
            throw
        }

        Write-Warning "Ignored ampy error: $Command"

        return 1
    }
}

function Ensure-RemoteDir {

    param(
        [string]$Dir
    )

    Invoke-Ampy "rmdir $Dir" -IgnoreErrors

    Write-Host "Create dir $Dir"

    Invoke-Ampy "mkdir $Dir"

    if ($LASTEXITCODE -ne 0) {

        Write-Error "Failed to create remote dir: $Dir"
        exit 1
    }
}

function Upload-File {

    param(
        [string]$Local,
        [string]$Remote
    )

    Write-Host "copying $Local -> $Remote"

    Invoke-Ampy "put `"$Local`" $Remote"

    if ($LASTEXITCODE -ne 0) {

        Write-Error "Upload failed: $Local"
        exit 1
    }
}

# ============================================================
# PYTHON FILES
# ============================================================

foreach ($_lib in $SRCS) {

    if ($_lib -ne ".") {
        Ensure-RemoteDir $_lib
    }

    $pattern =
        if ($_lib -eq ".") {
            "src/*.py"
        }
        else {
            "src/$_lib/*.py"
        }

    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue

    foreach ($_f in $files) {

        if ($_.Name -eq "setup.py") {
            continue
        }

        $_rf =
            if ($_lib -eq ".") {
                $_f.Name
            }
            else {
                "$_lib/$($_f.Name)"
            }

        $_mpy = [System.IO.Path]::ChangeExtension($_f.FullName, ".mpy")

        $compiled = $false

        # ----------------------------------------------------
        # COMPILE TO MPY
        # ----------------------------------------------------

        if ($USE_MPY -and $_f.Name -ne "main.py") {

            Write-Host "Compiling $($_f.Name)"

            python -m mpy_cross $_f.FullName

            if (($LASTEXITCODE -eq 0) -and (Test-Path $_mpy)) {

                $_remoteMpy =
                    if ($_lib -eq ".") {
                        [System.IO.Path]::GetFileName($_mpy)
                    }
                    else {
                        "$_lib/$([System.IO.Path]::GetFileName($_mpy))"
                    }

                Upload-File $_mpy $_remoteMpy

                Remove-Item $_mpy -Force

                $compiled = $true
            }
        }

        # ----------------------------------------------------
        # FALLBACK TO .PY
        # ----------------------------------------------------

        if (-not $compiled) {

            Upload-File $_f.FullName $_rf

            if (Test-Path $_mpy) {
                Remove-Item $_mpy -Force
            }
        }
    }
}

# ============================================================
# STATIC FILES
# ============================================================

foreach ($_lib in $HTMLS) {

    if ($_lib -ne ".") {
        Ensure-RemoteDir $_lib
    }

    foreach ($ext in @("html", "js", "css")) {

        Get-ChildItem "./$_lib/*.$ext" -ErrorAction SilentlyContinue | ForEach-Object {

            $_rf = "$_lib/$($_.Name)"

            if ($USE_MINIFY) {

                $_minified = "./src/$_lib/$($_.Name)"

                Write-Host "minify $($_.FullName)"

                minify $_.FullName |
                    Out-File $_minified -Encoding ascii

                Upload-File $_minified $_rf
            }
            else {

                Upload-File $_.FullName $_rf
            }
        }
    }
}

# ============================================================
# FAVICON
# ============================================================

if (Test-Path "static/favicon.ico") {

    Upload-File "static/favicon.ico" "static/favicon.ico"
}

# ============================================================
# FWUPD HOSTS
# ============================================================

Write-Host "Pushing FW-UPD host restrictions"

Invoke-Ampy "rmdir data" -IgnoreErrors
Invoke-Ampy "mkdir data"

Upload-File "src/fwupd.hosts" "data/fwupd.hosts"

# ============================================================
# DONE
# ============================================================

Write-Host ""
Write-Host "Flash completed successfully."