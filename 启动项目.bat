@echo off
chcp 65001 >nul
title 软著视觉自检助手 - CopyrightVisualMonitor

echo ========================================
echo    正在启动 CopyrightVisualMonitor...
echo ========================================

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python，请确保已安装并将其加入环境变量。
    pause
    exit /b
)

echo ✅ 环境检查成功！
echo.

echo 正在启动程序...
python main.py