@echo off
title QuickJPG Converter Installer
echo ==============================================
echo    Installing QuickJPG Converter for Windows 11
echo ==============================================
powershell.exe -ExecutionPolicy Bypass -File "%~dp0create_installer.ps1"
pause
