@echo off
REM ══════════════════════════════════════════════════════════
REM  Flujo - Ejecutar sin ventana de consola
REM ══════════════════════════════════════════════════════════

cd /d "%~dp0"
start pythonw app.py
exit
