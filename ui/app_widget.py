"""
应用音量控制小部件
"""

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QSlider, QPushButton, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AppWidget(QFrame):
    """单个应用的音量控制小部件"""
    
    def __init__(self, app_key, app_info, volume_controller, config,
                 is_auto_controlled=False, select_callback=None, selected=False):
        super().__init__()
        self.app_key = app_key
        self.app_info = app_info
        self.volume_controller = volume_controller
        self.config = config
        self.auto_controlled = is_auto_controlled
        self.select_callback = select_callback
        self.selected = selected
        
        self.init_ui()
        self.update_selected_state()
        self.update_auto_control_state(self.auto_controlled)
    
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(self.get_base_style())
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        display_name = self.app_info.get('display_name') or self.app_info.get('name') or self.app_key
        app_label = QLabel(display_name)
        app_label.setFont(QFont('Arial', 11, QFont.Bold))
        app_label.setMinimumWidth(180)
        
        self.status_label = QLabel()
        self.status_label.setFont(QFont('Arial', 8))
        self.status_label.setAlignment(Qt.AlignLeft)

        info_layout = QVBoxLayout()
        info_layout.addWidget(app_label)
        info_layout.addWidget(self.status_label)
        layout.addLayout(info_layout)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setMinimumWidth(220)
        
        try:
            current_volume = self.volume_controller.get_app_volume(self.app_key)
            if current_volume is not None:
                self.volume_slider.setValue(int(current_volume))
            else:
                self.volume_slider.setValue(self.config.get('default_volume', 50))
        except Exception:
            self.volume_slider.setValue(self.config.get('default_volume', 50))
        
        self.volume_slider.sliderMoved.connect(self.on_volume_changed)
        self.volume_slider.sliderReleased.connect(self.on_slider_released)
        layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel(f'{self.volume_slider.value()}%')
        self.volume_label.setMinimumWidth(40)
        self.volume_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.volume_label)
        
        reset_btn = QPushButton('重置')
        reset_btn.setMaximumWidth(60)
        reset_btn.clicked.connect(self.reset_volume)
        layout.addWidget(reset_btn)
        
        mute_btn = QPushButton('🔇 静音')
        mute_btn.setMaximumWidth(80)
        mute_btn.clicked.connect(self.toggle_mute)
        layout.addWidget(mute_btn)
    
    def get_base_style(self):
        return """
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                padding: 10px;
                margin: 5px 0px;
            }
        """
    
    def mousePressEvent(self, event):
        if self.select_callback:
            self.select_callback(self.app_key)
        super().mousePressEvent(event)
    
    def update_selected_state(self):
        if self.selected:
            self.setStyleSheet(self.get_base_style() + 'QFrame { border: 2px solid #4CAF50; }')
        else:
            self.setStyleSheet(self.get_base_style())
    
    def update_auto_control_state(self, allowed):
        self.auto_controlled = allowed
        if allowed:
            self.status_label.setText('自动控制: 是')
            self.status_label.setStyleSheet('color: #4CAF50;')
        else:
            self.status_label.setText('自动控制: 否')
            self.status_label.setStyleSheet('color: #888;')
    
    def set_selected(self, selected):
        self.selected = selected
        self.update_selected_state()
    
    def on_volume_changed(self, value):
        self.volume_label.setText(f'{value}%')
        self.update_app_volume(value)
    
    def on_slider_released(self):
        self.update_app_volume(self.volume_slider.value())
    
    def update_app_volume(self, volume):
        try:
            self.volume_controller.set_app_volume(self.app_key, volume)
        except Exception as e:
            print(f"设置 {self.app_key} 音量失败: {e}")
    
    def set_volume(self, volume):
        self.volume_slider.setValue(volume)
        self.volume_label.setText(f'{volume}%')
        self.update_app_volume(volume)
    
    def reset_volume(self):
        default_volume = self.config.get('default_volume', 50)
        self.volume_slider.setValue(default_volume)
        self.volume_label.setText(f'{default_volume}%')
        self.update_app_volume(default_volume)
    
    def toggle_mute(self):
        try:
            self.volume_controller.toggle_mute(self.app_key)
        except Exception as e:
            print(f"切换 {self.app_key} 静音失败: {e}")
