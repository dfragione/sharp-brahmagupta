# Windows 11 Installer for PixShift Image Converter
$ErrorActionPreference = "Stop"

$AppName = "PixShift Image Converter"
$ExeName = "PixShift.exe"
$SourceDir = $PSScriptRoot
$SourceExe = Join-Path $SourceDir "dist\$ExeName"

if (-not (Test-Path $SourceExe)) {
    $SourceExe = Join-Path $SourceDir "$ExeName"
}

if (-not (Test-Path $SourceExe)) {
    Write-Host "Executable not found. Building it now..." -ForegroundColor Yellow
    python $SourceDir\build_exe.py
    $SourceExe = Join-Path $SourceDir "dist\$ExeName"
}

$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\PixShift"
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Installing $AppName on Windows 11   " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Create install directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

# 2. Copy binary and assets
Write-Host "Copying files to $InstallDir..." -ForegroundColor Green
Copy-Item -Path $SourceExe -Destination $InstallDir -Force

$AssetsSrc = Join-Path $SourceDir "assets"
if (Test-Path $AssetsSrc) {
    Copy-Item -Path $AssetsSrc -Destination $InstallDir -Recurse -Force
}

$TargetExe = Join-Path $InstallDir $ExeName

# 3. Create Start Menu Shortcut
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$WshShell = New-Object -ComObject WScript.Shell

$StartShortcutPath = Join-Path $StartMenuDir "$AppName.lnk"
$Shortcut = $WshShell.CreateShortcut($StartShortcutPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "PixShift Image Converter for Windows 11 (JPG, WEBP, AVIF)"
$Shortcut.IconLocation = "$TargetExe,0"
$Shortcut.Save()
Write-Host "Created Start Menu Shortcut: $StartShortcutPath" -ForegroundColor Green

# 4. Create Desktop Shortcut
$DesktopDir = [Environment]::GetFolderPath("Desktop")
$DesktopShortcutPath = Join-Path $DesktopDir "$AppName.lnk"
$Shortcut = $WshShell.CreateShortcut($DesktopShortcutPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "PixShift Image Converter for Windows 11 (JPG, WEBP, AVIF)"
$Shortcut.IconLocation = "$TargetExe,0"
$Shortcut.Save()
Write-Host "Created Desktop Shortcut: $DesktopShortcutPath" -ForegroundColor Green

Write-Host "`nInstallation Completed Successfully!" -ForegroundColor Cyan
Write-Host "You can now launch PixShift directly from your Desktop or Start Menu without Python." -ForegroundColor Cyan
