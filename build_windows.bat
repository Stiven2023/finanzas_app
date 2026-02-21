@echo off
setlocal

set PY=D:\Programación\Finanzas\Finanzas2026_App\finanzas_app\.venv\Scripts\python.exe

echo [1/2] Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Flujo.spec del /q Flujo.spec

echo [2/2] Generando ejecutable...
"%PY%" -m PyInstaller --noconfirm --clean --windowed --name Flujo app.py

echo.
echo Build finalizado. Ejecutable: dist\Flujo\Flujo.exe
pause
