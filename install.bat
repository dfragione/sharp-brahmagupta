@echo off
title PixShift Image Converter Installer
echo ==============================================
echo    Installing PixShift Converter for Windows 11
echo ==============================================
powershell.exe -ExecutionPolicy Bypass -File "%~dp0create_installer.ps1"
pause
