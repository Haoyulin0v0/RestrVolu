"""
音量控制工具 - 主应用
自动监听系统应用，并对新打开的应用进行音量控制
"""

import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from comtypes import CoInitialize, CoUninitialize
from ui.main_window import MainWindow

# 配置文件路径
CONFIG_DIR = Path.home() / '.volume_control'
CONFIG_FILE = CONFIG_DIR / 'config.json'

def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """加载配置文件"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_config()

def get_default_config():
    """获取默认配置"""
    return {
        'default_volume': 50,
        'auto_control_enabled': True,
        'monitored_apps': {},
        'theme': 'light'
    }

def save_config(config):
    """保存配置文件"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    # 在主线程中初始化COM
    CoInitialize()
    try:
        app = QApplication(sys.argv)
        
        # 加载配置
        config = load_config()
        
        # 创建主窗口
        window = MainWindow(config)
        window.show()
        
        sys.exit(app.exec_())
    finally:
        CoUninitialize()

if __name__ == '__main__':
    main()
