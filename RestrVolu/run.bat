@echo off
REM 快速启动脚本 - 音量控制工具
REM 此脚本会安装依赖并运行应用

echo ========================================
echo   音量控制工具 - 快速启动
echo ========================================
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python已安装

REM 检查是否需要安装依赖
echo.
echo 正在检查依赖...
pip show PyQt5 > nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少依赖，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ✗ 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo ✓ 所有依赖已准备就绪
echo.
echo 启动音量控制工具...
echo.

REM 运行应用
python main.py

pause
