
param(
    [Parameter(Mandatory = $true)]
    [string]$Port,

    [string]$Board = "esp32.json",

    [switch]$Force
)

$ErrorActionPreference = "Stop"

$CACHE_FILE = ".flash_cache.json"
$RemoteDirCache = @{}
$FileCache = @{}

if ((Test-Path $CACHE_FILE) -and (-not $Force)) {
    try {
        $FileCache = Get-Content $CACHE_FILE -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        $FileCache = @{}
    }
}

$SRCS = @(
    "hw",
    "hw/$([System.IO.Path]::GetFileNameWithoutExtension($Board))",
    "net",
    "uclient",
    "certs",
    "."
)

$HTMLS = @("static")

function Get-Hash {
    param([string]$Path)
    return (Get-FileHash $Path -Algorithm SHA256).Hash
}

function Save-Cache {
    $FileCache | ConvertTo-Json -Depth 5 | Out-File $CACHE_FILE -Encoding utf8
}

function Invoke-Ampy {
    param([string]$Command,[switch]$IgnoreErrors)

    try {
        Invoke-Expression "ampy --delay 1 -p $Port $Command 2>&1" | Out-Host
        return $LASTEXITCODE
    }
    catch {
        if (-not $IgnoreErrors) { throw }
        return 1
    }
}

function Ensure-RemoteDir {
    param([string]$Dir)

    if ($RemoteDirCache.ContainsKey($Dir)) { return }

    $parts = $Dir -split '/'
    $current = ""

    foreach ($part in $parts) {
        if ([string]::IsNullOrWhiteSpace($part)) { continue }

        if ($current) { $current += "/$part" }
        else { $current = $part }

        Invoke-Ampy "mkdir $current" -IgnoreErrors | Out-Null
    }

    $RemoteDirCache[$Dir] = $true
}

function Upload-IfChanged {
    param(
        [string]$LocalFile,
        [string]$RemoteFile
    )

    $hash = Get-Hash $LocalFile

    if ((-not $Force) -and
        $FileCache.ContainsKey($RemoteFile) -and
        $FileCache[$RemoteFile] -eq $hash) {

        Write-Host "SKIP  $RemoteFile"
        return
    }

    Write-Host "UPLOAD $RemoteFile"

    Invoke-Ampy "put `"$LocalFile`" $RemoteFile"

    if ($LASTEXITCODE -ne 0) {
        throw "Upload failed: $RemoteFile"
    }

    $FileCache[$RemoteFile] = $hash
}

# tool checks
if (!(Get-Command ampy -ErrorAction SilentlyContinue)) { throw "ampy not found" }
if (!(Get-Command python -ErrorAction SilentlyContinue)) { throw "python not found" }

$USE_MINIFY = [bool](Get-Command minify -ErrorAction SilentlyContinue)

$USE_MPY = $false
try {
    python -m mpy_cross --help *> $null
    if ($LASTEXITCODE -eq 0) { $USE_MPY = $true }
} catch {}

# board generation
if (Test-Path "src/board.py") { Remove-Item "src/board.py" -Force }

$json = Get-Content $Board -Raw | ConvertFrom-Json
$json | ConvertTo-Json -Depth 100 | python tools/json2py.py | Out-File "src/board.py" -Encoding ascii

$arch = [System.IO.Path]::GetFileNameWithoutExtension($Board)
"ARCH = `"$arch`"" | Out-File "src/hw/arch.py" -Encoding ascii

foreach ($_lib in $SRCS) {

    if ($_lib -ne ".") { Ensure-RemoteDir $_lib }

    $pattern =
        if ($_lib -eq ".") { "src/*.py" }
        elseif ($_lib -eq "certs") { "src/certs/*.der" }
        else { "src/$_lib/*.py" }

    Get-ChildItem $pattern -ErrorAction SilentlyContinue | ForEach-Object {

        $_f = $_

        if ($_lib -eq "certs") {
            Upload-IfChanged $_f.FullName "$_lib/$($_f.Name)"
            return
        }

        $_mpy = [System.IO.Path]::ChangeExtension($_f.FullName, ".mpy")

        if ($USE_MPY -and $_f.Name -ne "main.py") {

            python -m mpy_cross $_f.FullName

            if (($LASTEXITCODE -eq 0) -and (Test-Path $_mpy)) {

                $remote =
                    if ($_lib -eq ".") {
                        [IO.Path]::GetFileName($_mpy)
                    } else {
                        "$_lib/$([IO.Path]::GetFileName($_mpy))"
                    }

                Upload-IfChanged $_mpy $remote
                Remove-Item $_mpy -Force
                return
            }
        }

        $remote =
            if ($_lib -eq ".") { $_f.Name }
            else { "$_lib/$($_f.Name)" }

        Upload-IfChanged $_f.FullName $remote
    }
}

foreach ($_lib in $HTMLS) {

    Ensure-RemoteDir $_lib

    foreach ($ext in @("html","js","css")) {

        Get-ChildItem "./$_lib/*.$ext" -ErrorAction SilentlyContinue | ForEach-Object {

            if ($USE_MINIFY) {

                $tmp = Join-Path $env:TEMP ("min_" + $_.Name)

                minify $_.FullName | Out-File $tmp -Encoding ascii

                Upload-IfChanged $tmp "$_lib/$($_.Name)"

                Remove-Item $tmp -Force -ErrorAction SilentlyContinue
            }
            else {
                Upload-IfChanged $_.FullName "$_lib/$($_.Name)"
            }
        }
    }
}

if (Test-Path "static/favicon.ico") {
    Upload-IfChanged "static/favicon.ico" "static/favicon.ico"
}

Ensure-RemoteDir "data"

if (Test-Path "src/fwupd.hosts") {
    Upload-IfChanged "src/fwupd.hosts" "data/fwupd.hosts"
}

Save-Cache

Write-Host ""
Write-Host "Flash completed successfully."
