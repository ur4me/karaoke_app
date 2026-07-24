#!/bin/bash
# 더블클릭으로 노래방 앱을 실행하는 파일입니다.
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "❌ Python이 설치되어 있지 않습니다. https://www.python.org 에서 설치해주세요."
    read -p "엔터를 누르면 창이 닫힙니다..." _
    exit 1
fi

echo "🎤 노래방 앱을 시작합니다... (이 창을 닫으면 앱이 종료됩니다)"
"$PYTHON" main.py

read -p "엔터를 누르면 창이 닫힙니다..." _
