param(
    [string]$AwsIotEndpoint = "a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com",
    [string]$AwsRegion = "eu-central-1",
    [string]$AwsIotCaFile = "C:\Users\aubal\workspace\personal\roboscine\config\cert\AmazonRootCA1.pem",
    [string]$AwsIotCertFile = "C:\Users\aubal\workspace\personal\roboscine\config\cert\certificate.pem.crt",
    [string]$AwsIotKeyFile = "C:\Users\aubal\workspace\personal\roboscine\config\cert\private_pkcs8.pem",
    [string]$MqttClientId = "roboscine-sync-emulator",
    [string]$DeviceMac = "48:3f:da:55:07:5b",
    [string]$DeviceSerial = "3996365525",
    [string]$LogLevel = "INFO",
    [switch]$InstallOnly,
    [switch]$SkipVenv
)

$ErrorActionPreference = "Stop"

$scriptDir = (Resolve-Path $PSScriptRoot).Path
$venvDir = Join-Path $scriptDir ".venv"
$pythonFromVenv = Join-Path $venvDir "Scripts\python.exe"

if ([string]::IsNullOrWhiteSpace($AwsIotEndpoint)) {
    throw "Parameter -AwsIotEndpoint is required. Example: -AwsIotEndpoint 'a1b2c3d4e5f6g7-ats.iot.eu-central-1.amazonaws.com'"
}

if (-not (Test-Path $AwsIotCaFile)) {
    throw "AWS IoT CA file not found: $AwsIotCaFile"
}
if (-not (Test-Path $AwsIotCertFile)) {
    throw "AWS IoT certificate file not found: $AwsIotCertFile"
}
if (-not (Test-Path $AwsIotKeyFile)) {
    throw "AWS IoT private key file not found: $AwsIotKeyFile"
}

Push-Location $scriptDir
try {
    if (-not $SkipVenv) {
        if (-not (Test-Path $pythonFromVenv)) {
            Write-Host "[emulator] Creating virtual environment..." -ForegroundColor Cyan
            python -m venv .venv
        }

        Write-Host "[emulator] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
        & $pythonFromVenv -m pip install -r requirements.txt | Out-Host
        $pythonCmd = $pythonFromVenv
    }
    else {
        Write-Host "[emulator] Using system python (SkipVenv enabled)..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt | Out-Host
        $pythonCmd = "python"
    }

    # Export environment variables expected by device_emulator.py
    $env:AWS_IOT_ENDPOINT = $AwsIotEndpoint
    $env:AWS_REGION = $AwsRegion
    $env:AWS_IOT_CA_FILE = $AwsIotCaFile
    $env:AWS_IOT_CERT_FILE = $AwsIotCertFile
    $env:AWS_IOT_KEY_FILE = $AwsIotKeyFile
    $env:MQTT_CLIENT_ID = $MqttClientId
    $env:DEVICE_MAC = $DeviceMac
    $env:DEVICE_SERIAL = $DeviceSerial
    $env:LOG_LEVEL = $LogLevel

    Write-Host "[emulator] Environment prepared:" -ForegroundColor Green
    Write-Host "  AWS_IOT_ENDPOINT=$($env:AWS_IOT_ENDPOINT)"
    Write-Host "  AWS_REGION=$($env:AWS_REGION)"
    Write-Host "  AWS_IOT_CA_FILE=$($env:AWS_IOT_CA_FILE)"
    Write-Host "  AWS_IOT_CERT_FILE=$($env:AWS_IOT_CERT_FILE)"
    Write-Host "  AWS_IOT_KEY_FILE=$($env:AWS_IOT_KEY_FILE)"
    Write-Host "  DEVICE_MAC=$($env:DEVICE_MAC)"
    Write-Host "  DEVICE_SERIAL=$($env:DEVICE_SERIAL)"

    if ($InstallOnly) {
        Write-Host "[emulator] InstallOnly mode: device_emulator.py was not started." -ForegroundColor Yellow
        return
    }

    Write-Host "[emulator] Starting device_emulator.py..." -ForegroundColor Green
    if ($SkipVenv) {
        python device_emulator.py
    }
    else {
        & $pythonFromVenv device_emulator.py
    }
}
finally {
    Pop-Location
}

