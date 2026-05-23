"""
构建脚本 - 打包成EXE
使用PyInstaller将应用打包成Windows可执行文件
"""

import os
import shutil
import subprocess
from pathlib import Path

def build_exe():
    """构建EXE文件"""
    
    project_dir = Path(__file__).parent
    dist_dir = project_dir / 'dist'
    build_dir = project_dir / 'build'
    
    # 清理之前的构建
    print("清理之前的构建文件...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller命令
    print("开始构建EXE文件...")
    cmd = [
        'pyinstaller',
        '--onefile',  # 单文件
        '--windowed',  # 无控制台窗口
        '--name=VolumeControl',  # 应用名称
        '--icon=INFILE:icon.ico' if (project_dir / 'icon.ico').exists() else '',
        '--add-data=ui:ui',
        '--add-data=core:core',
        '--hidden-import=pycaw',
        '--hidden-import=comtypes',
        '--hidden-import=psutil',
        str(project_dir / 'main.py')
    ]
    
    # 移除空的参数
    cmd = [c for c in cmd if c]
    
    try:
        subprocess.run(cmd, check=True, cwd=str(project_dir))
        print("✓ EXE构建成功！")
        print(f"输出位置: {dist_dir / 'VolumeControl.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("✗ PyInstaller未安装，请运行: pip install PyInstaller")
        return False
    
    return True

if __name__ == '__main__':
    build_exe()
