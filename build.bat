@echo off
REM 打包脚本 - 将应用打包成EXE
REM 此脚本会检查环境并构建EXE文件

echo ========================================
echo   音量控制工具 - EXE打包
echo ========================================
echo.

REM 检查Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ 错误: 未找到Python
    pause
    exit /b 1
)

echo ✓ Python已安装

REM 检查PyInstaller
echo.
echo 检查PyInstaller...
pip show PyInstaller > nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少PyInstaller，正在安装...
    pip install PyInstaller
)

echo.
echo 正在构建EXE文件，这可能需要几分钟...
echo.

REM 运行构建脚本
python build.py

if %errorlevel% equ 0 (
    echo.
    echo ✓ 构建成功！
    echo.
    echo EXE文件位置: dist\VolumeControl.exe
    echo.
    echo 你现在可以:
    echo 1. 直接运行 dist\VolumeControl.exe
    echo 2. 将其复制到任何位置使用
    echo 3. 在其他电脑上运行（无需Python）
) else (
    echo.
    echo ✗ 构建失败
)

pause
