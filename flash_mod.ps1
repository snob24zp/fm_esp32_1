param(
    [Parameter(Mandatory = $true)]
    [string]$Port,

    [string]$Board = "esp32.json",

    # Добавлен флаг для принудительной прошивки всех файлов при необходимости
    [switch]$Force
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

# Путь к файлу кэша хешей
$CACHE_FILE = "./.flash_cache.json"

# Хеш-таблица для хранения состояния файлов
$ScriptCache = @{}
if ((Test-Path $CACHE_FILE) -and (-not $Force)) {
    try {
        $ScriptCache = Get-Content $CACHE_FILE -Raw | ConvertFrom-Json -AsHashtable
        Write-Host "Loaded file cache. Only changed files will be uploaded." -ForegroundColor Cyan
    } catch {
        $ScriptCache = @{}
    }
} elseif ($Force) {
    Write-Host "Force flag detected. Full re-upload started." -ForegroundColor Yellow
}

# Функция проверки: изменился ли файл?
function Should-UploadFile {
    param (
        [string]$FilePath
    )
    if ($Force) { return $true }
    
    # Считаем SHA256 хеш файла
    $currentHash = (Get-FileHash $FilePath -Algorithm SHA256).Hash
    
    # Если файла нет в кэше или хеш изменился
    if (-not $ScriptCache.ContainsKey($FilePath) -or $ScriptCache[$FilePath] -ne $currentHash) {
        # Обновляем хеш в памяти (сохраним в файл в самом конце скрипта)
        $ScriptCache[$FilePath] = $currentHash
        return $true
    }
    return $false
}

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

# ============================================================
# AMPY WRAPPERS
# ============================================================

function Invoke-Ampy {
    param(
        [string]$Command,
        [switch]$IgnoreErrors
    )

    $ampyCmd = "ampy --port $Port --baud 115200 $Command"
    
    if ($IgnoreErrors) {
        Invoke-Expression $ampyCmd 2>$null
    }
    else {
        Invoke-Expression $ampyCmd
    }
}

function Ensure-RemoteDir {
    param([string]$Dir)
    
    $parts = $Dir -split '/'
    $current = ""
    foreach ($part in $parts) {
        if ([string]::IsNullOrEmpty($part) -or $part -eq ".") { continue }
        if ($current -eq "") { $current = $part }
        else { $current = "$current/$part" }
        
        Invoke-Ampy "mkdir $current" -IgnoreErrors
    }
}

function Upload-File {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )

    Write-Host "Uploading: $LocalPath -> $RemotePath" -ForegroundColor Green
    Invoke-Ampy "put $LocalPath $RemotePath"
}

# ============================================================
# SOURCE CODE UPLOAD (.py files)
# ============================================================

foreach ($_dir in $SRCS) {

    Get-ChildItem "$_dir/*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        
        # Проверяем, изменился ли исходный python-файл
        if (Should-UploadFile $_.FullName) {
            if ($_dir -eq ".") {
                $_rf = $_.Name
            }
            else {
                Ensure-RemoteDir $_dir
                $_rf = "$_dir/$($_.Name)"
            }

            Upload-File $_.FullName $_rf
        } else {
            Write-Host "Skipped (Unchanged): $($_.Name)" -ForegroundColor Gray
        }
    }
}

# ============================================================
# STATIC FILES UPLOAD (html, js, css)
# ============================================================

if ($USE_MINIFY) {
    Ensure-RemoteDir "src/static"
}

foreach ($_lib in $HTMLS) {

    if ($_lib -ne \".\") {
        Ensure-RemoteDir $_lib
    }

    foreach ($ext in @("html", "js", "css")) {

        Get-ChildItem "./$_lib/*.$ext" -ErrorAction SilentlyContinue | ForEach-Object {

            $_rf = "$_lib/$($_.Name)"

            # Проверяем оригинальный файл по кэшу хешей
            if (Should-UploadFile $_.FullName) {
                
                if ($USE_MINIFY) {
                    $_minified = "./src/$_lib/$($_.Name)"
                    Write-Host "Minifying $($_.FullName)..." -ForegroundColor Magenta
                    
                    # Сжимаем файл во временную директорию
                    minify $_.FullName | Out-File $_minified -Encoding ascii
                    
                    # Прошиваем минифицированную версию
                    Upload-File $_minified $_rf
                }
                else {
                    Upload-File $_.FullName $_rf
                }
            } else {
                Write-Host "Skipped (Unchanged): $_rf" -ForegroundColor Gray
            }
        }
    }
}

# ============================================================
# FAVICON
# ============================================================

if (Test-Path "static/favicon.ico") {
    if (Should-UploadFile "static/favicon.ico") {
        Upload-File "static/favicon.ico" "static/favicon.ico"
    }
}

# ============================================================
# FWUPD HOSTS
# ============================================================

if (Test-Path "src/fwupd.hosts") {
    if (Should-UploadFile "src/fwupd.hosts") {
        Write-Host "Pushing FW-UPD host restrictions"
        Invoke-Ampy "rmdir data" -IgnoreErrors
        Invoke-Ampy "mkdir data"
        Upload-File "src/fwupd.hosts" "data/fwupd.hosts"
    }
}

# ============================================================
# SAVE CACHE STATE
# ============================================================
# Сохраняем обновленную таблицу хешей обратно в файл
$ScriptCache | ConvertTo-Json | Out-File $CACHE_FILE -Encoding utf8

Write-Host "Flash process completed successfully!" -ForegroundColor Cyan