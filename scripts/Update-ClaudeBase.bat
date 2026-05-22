@echo off
REM === Updater 2.0 для claude-base ===
REM Двойной клик → запускает Update-ClaudeBase.ps1 в Windows PowerShell 5.1
REM с UTF-8 console output и bypass execution policy.

chcp 65001 > nul
title Update-ClaudeBase 2.0

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Update-ClaudeBase.ps1"

echo.
echo === Updater завершён. Нажмите любую клавишу чтобы закрыть окно ===
pause > nul
