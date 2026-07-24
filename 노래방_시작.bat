@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    set PYCMD=python
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set PYCMD=py
    ) else (
        echo Python이 설치되어 있지 않습니다. https://www.python.org 에서 설치해주세요.
        pause
        exit /b 1
    )
)

echo 노래방 앱을 시작합니다... (이 창을 닫으면 앱이 종료됩니다)
%PYCMD% main.py

pause
