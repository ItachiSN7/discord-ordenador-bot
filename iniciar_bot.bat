@echo off
title Bot Ordenador
cd /d "%~dp0"
echo ============================================
echo   Iniciando bot Ordenador (!uniforme / !armas)
echo   Deja esta ventana abierta. Ctrl+C para parar.
echo ============================================
py bot.py
echo.
echo El bot se ha detenido. Pulsa una tecla para cerrar.
pause >nul
