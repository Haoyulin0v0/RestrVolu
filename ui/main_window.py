"""
主窗口UI模块
"""

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QScrollArea, QFrame, QCheckBox, QSpinBox, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt5.QtCore import QSize
from comtypes import CoInitialize, CoUninitialize

from core.volume_controller import VolumeController
from core.process_monitor import ProcessMonitor
from ui.app_widget import AppWidget

class ProcessMonitorThread(QThread):
    """进程监听线程"""
    apps_updated = pyqtSignal(dict)
    
    def __init__(self, volume_controller):
        super().__init__()
        self.volume_controller = volume_controller
        self.running = True
        self.last_apps = {}
    
    def run(self):
        """监听循环"""
        # 在线程中初始化COM
        CoInitialize()
        try:
            monitor = ProcessMonitor()
            while self.running:
                try:
                    current_apps = monitor.get_audio_apps()
                    if current_apps != self.last_apps:
                        self.last_apps = current_apps
                        self.apps_updated.emit(current_apps)
                    self.msleep(1000)  # 每秒检查一次
                except Exception as e:
                    print(f"监听错误: {e}")
        finally:
            # 清理COM
            CoUninitialize()
    
    def stop(self):
        """停止监听"""
        self.running = False

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.volume_controller = VolumeController()
        self.monitor_thread = None
        self.app_widgets = {}
        
        self.init_ui()
        self.setup_monitoring()
        self.setStyleSheet(self.get_stylesheet())
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('🔊 音量控制工具')
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 400)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title = QLabel('🔊 系统音量控制')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        main_layout.addWidget(title)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 应用音量标签页
        self.apps_tab = QWidget()
        self.apps_layout = QVBoxLayout(self.apps_tab)
        
        # 可滚动的应用列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.apps_scroll_layout = QVBoxLayout(scroll_widget)
        self.apps_scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        self.apps_layout.addWidget(scroll)
        
        self.tab_widget.addTab(self.apps_tab, '🎵 应用音量')
        
        # 设置标签页
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # 默认音量设置
        settings_layout.addWidget(QLabel('默认应用音量 (%)'))
        default_vol_layout = QHBoxLayout()
        self.default_volume_spin = QSpinBox()
        self.default_volume_spin.setRange(0, 100)
        self.default_volume_spin.setValue(self.config.get('default_volume', 50))
        self.default_volume_spin.valueChanged.connect(self.on_default_volume_changed)
        default_vol_layout.addWidget(self.default_volume_spin)
        default_vol_layout.addStretch()
        settings_layout.addLayout(default_vol_layout)
        
        # 自动控制开关
        settings_layout.addSpacing(10)
        self.auto_control_checkbox = QCheckBox('启用自动音量控制')
        self.auto_control_checkbox.setChecked(self.config.get('auto_control_enabled', True))
        self.auto_control_checkbox.stateChanged.connect(self.on_auto_control_toggled)
        settings_layout.addWidget(self.auto_control_checkbox)
        
        settings_layout.addSpacing(10)
        help_text = QLabel(
            '💡 提示:\n'
            '• 启用自动控制后，新打开的应用将自动降音量\n'
            '• 你可以为每个应用单独调整音量\n'
            '• 设置会自动保存'
        )
        help_text.setFont(QFont('Arial', 9))
        help_text.setStyleSheet('color: #666; line-height: 1.5;')
        settings_layout.addWidget(help_text)
        
        settings_layout.addStretch()
        
        self.tab_widget.addTab(settings_tab, '⚙️ 设置')
    
    def setup_monitoring(self):
        """设置进程监听"""
        self.monitor_thread = ProcessMonitorThread(self.volume_controller)
        self.monitor_thread.apps_updated.connect(self.update_app_widgets)
        self.monitor_thread.start()
    
    def update_app_widgets(self, apps):
        """更新应用列表"""
        # 移除不存在的会话（按会话键）
        for app_key in list(self.app_widgets.keys()):
            if app_key not in apps:
                widget = self.app_widgets[app_key]
                self.apps_scroll_layout.removeWidget(widget)
                widget.deleteLater()
                del self.app_widgets[app_key]

        # 添加新会话
        for app_key, app_info in apps.items():
            if app_key not in self.app_widgets:
                widget = AppWidget(app_key, app_info, self.volume_controller, self.config)
                # 在stretch之前插入
                index = self.apps_scroll_layout.count() - 1
                self.apps_scroll_layout.insertWidget(index, widget)
                self.app_widgets[app_key] = widget

                # 自动控制：如果启用，则立即应用默认音量到新会话
                if self.config.get('auto_control_enabled', True):
                    try:
                        default_vol = self.config.get('default_volume', 50)
                        # 先静音，防止突发高音量，然后设置默认音量，稍后取消静音
                        self.volume_controller.set_app_mute(app_key, True)
                        self.volume_controller.set_app_volume(app_key, default_vol)
                        # 250ms 后取消静音以确保设置生效并避免音爆
                        QTimer.singleShot(250, lambda key=app_key: self.volume_controller.set_app_mute(key, False))
                    except Exception as e:
                        print(f"自动设置默认音量失败 ({app_key}): {e}")
    
    def on_default_volume_changed(self, value):
        """默认音量改变"""
        self.config['default_volume'] = value
        self.save_config()
    
    def on_auto_control_toggled(self, state):
        """自动控制开关改变"""
        self.config['auto_control_enabled'] = state == Qt.Checked
        self.save_config()
    
    def save_config(self):
        """保存配置"""
        from main import save_config
        save_config(self.config)
    
    def get_stylesheet(self):
        """获取样式表"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QSlider::groove:horizontal {
                background-color: #e0e0e0;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #4CAF50;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #45a049;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
            QFrame {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 6px 20px;
            }
            QTabBar::tab:selected {
                background-color: white;
            }
            QSpinBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 3px;
            }
        """
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        event.accept()
