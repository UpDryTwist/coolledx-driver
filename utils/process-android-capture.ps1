Param(
    [Parameter(Mandatory=$false)]
    [string]$CoolledMac = "ff:00:00:04:25:ab",
    [Parameter(Mandatory=$false)]
    [string]$TempPath = "D:\temp",
    [Parameter(Mandatory=$false)]
    [string]$PacketCaptureFileName = "btsnoop_hci.log",
    [Parameter(Mandatory=$false)]
    [string]$AdbExe = "adb",
    [Parameter(Mandatory=$false)]
    [string]$ProcessedFileName = "coolled_btlog.txt",
    [Parameter(Mandatory=$false)]
    [string]$Registry = "registry.supercroy.com/updrytwist",
    [Parameter(Mandatory=$false)]
    [string]$7ZipExe = "$env:ProgramFiles\7-Zip\7z.exe"
)
# Script to capture ADB bugreport and extract Bluetooth logs
# Ensure ADB is in your system PATH
# Your Android device should be connected with ADB debugging enabled
# Parameters:
# - CoolledMac: MAC address of the CoolLED device
# - TempPath: Temporary directory to store files
# - PacketCaptureFileName: Name of the packet capture file
# - AdbExe: Path to ADB executable
# - ProcessedFileName: Name of the processed file
# - Registry: Docker registry to pull the image from
# - 7ZipExe: Path to 7-Zip executable - empty to use Expand-Archive

# Pick your favorite bash shell . . .
# $BASH="wsl bash"
# $BASH="d:\programs\git\bin\bash.exe -c"
# $BASH="c:\cygwin64\bin\bash.exe -c"

if (-not (Test-Path "${7ZipExe}" -PathType Leaf)) {
    $7ZipExe=""
} else {
    Set-Alias Run-SevenZip $7ZipExe
}
Set-Alias Run-ADB $AdbExe

# Function to play sound notification
function Play-NotificationSound {
    [System.Console]::Beep(800, 500)  # Frequency: 800Hz, Duration: 500ms
}

# Function to show Windows notification
function Show-Notification {
    param([string]$Title, [string]$Message)

    Add-Type -AssemblyName System.Windows.Forms
    $global:balloon = New-Object System.Windows.Forms.NotifyIcon
    $path = (Get-Process -id $pid).Path
    $balloon.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($path)
    $balloon.Visible = $true
    $balloon.ShowBalloonTip(5000, $Title, $Message, [System.Windows.Forms.ToolTipIcon]::Info)
}

# Create temp directory if it doesn't exist
if (-not (Test-Path "${TempPath}")) {
    New-Item -ItemType Directory -Path "${TempPath}"
}

# Set working directory
$originalPath = Get-Location
Set-Location "${TempPath}"

# Get current timestamp for unique filename
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$bugreportFile = "bugreport_$timestamp"

$bugreportFile = "bugreport_20241208_002912"
$bugreportZip = "$bugreportFile.zip"
$packetCaptureFile = "${TempPath}\${bugreportFile}\FS\data\log\bt\${PacketCaptureFileName}"
$extractedFile="${TempPath}\${PacketCaptureFileName}"
$processedFilePath="${TempPath}\${ProcessedFileName}"

# Run ADB bugreport command
# Write-Host "Capturing bug report... This may take a few minutes."
# Run-ADB bugreport $bugreportZip

# Check if bugreport was created successfully
if (-not (Test-Path $bugreportZip)) {
    Write-Error "Failed to generate bugreport. Make sure device is connected and ADB is working."
    Show-Notification "ADB Bugreport Error" "Failed to generate bugreport"
    Play-NotificationSound
    exit 1
}

# Extract the Bluetooth log file
Write-Host "Extracting Bluetooth logs..."
try {
    Write-Host "Extracting ${PacketCaptureFileName} from ${bugreportZip}..."
    if ( ${7ZIP} -ne "" ) {
        Write-Host "Using 7-Zip to extract files..."
        Run-SevenZip x -o"$bugreportFile" $bugreportZip -y -aoa
    } else {
        Write-Host "Using Expand-Archive to extract files..."
        Expand-Archive -Path $bugreportZip -DestinationPath "$bugreportFile" -Force
    }
    Write-Host "Copying $packetCaptureFile to $extractedFile ..."
    Copy-Item $packetCaptureFile -Destination "${extractedFile}" -Force
    Write-Host "Successfully extracted ${packetCaptureFile} to ${TempPath}"

    # Use the docker image to scan for bluetooth devices
    docker pull ${Registry}/coolledx:latest

#        –cap-add=NET_RAW –cap-add=NET_ADMIN `

    docker run --privileged `
        -v ${TempPath}:/tmp `
        "${Registry}/coolledx:latest" `
        python3 /app/utils/bt_analyzer.py -f "/tmp/${PacketCaptureFileName}" -a "${CoolledMac}" > $processedFilePath

} catch {
    Write-Error "Error extracting files: $_"
    Show-Notification "ADB Bugreport Error" "Error extracting files"
    Play-NotificationSound
} finally {
    # Clean up temporary files
    if (Test-Path $bugreportFile) {
        Remove-Item -Path $bugreportFile -Recurse -Force
    }
    Set-Location -Path $originalPath
}

# Clean up notification icon
$global:balloon.Dispose()
