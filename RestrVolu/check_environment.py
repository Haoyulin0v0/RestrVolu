"""
环境检查脚本
验证所有依赖和配置是否正确安装
"""

import sys
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python版本过低，需要 3.7 或更高")
        return False
    
    print("✓ Python版本正确")
    return True

def check_imports():
    """检查依赖是否已安装"""
    packages = [
        ('PyQt5', 'PyQt5.QtWidgets'),
        ('pycaw', 'pycaw'),
        ('psutil', 'psutil'),
        ('comtypes', 'comtypes'),
    ]
    
    all_ok = True
    for name, module in packages:
        try:
            __import__(module)
            print(f"✓ {name} - 已安装")
        except ImportError:
            print(f"❌ {name} - 未安装")
            print(f"   运行: pip install {name}")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """检查项目结构"""
    required_files = [
        'main.py',
        'requirements.txt',
        'core/volume_controller.py',
        'core/process_monitor.py',
        'ui/main_window.py',
        'ui/app_widget.py',
    ]
    
    project_dir = Path(__file__).parent
    all_ok = True
    
    for file in required_files:
        file_path = project_dir / file
        if file_path.exists():
            print(f"✓ {file} - 存在")
        else:
            print(f"❌ {file} - 缺失")
            all_ok = False
    
    return all_ok

def main():
    """主检查函数"""
    print("="*50)
    print("音量控制工具 - 环境检查")
    print("="*50)
    print()
    
    print("1. 检查Python版本")
    print("-"*50)
    check1 = check_python_version()
    print()
    
    print("2. 检查依赖包")
    print("-"*50)
    check2 = check_imports()
    print()
    
    print("3. 检查项目结构")
    print("-"*50)
    check3 = check_project_structure()
    print()
    
    print("="*50)
    if check1 and check2 and check3:
        print("✓ 所有检查通过！可以运行应用")
        print()
        print("运行应用:")
        print("  python main.py")
        return True
    else:
        print("❌ 存在问题，请按上面的提示解决")
        print()
        print("如果问题仍未解决，运行:")
        print("  pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
