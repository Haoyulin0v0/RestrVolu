"""
应用音量控制小部件
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QPushButton, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AppWidget(QFrame):
    """单个应用的音量控制小部件"""
    
    def __init__(self, app_key, app_info, volume_controller, config):
        super().__init__()
        # app_key 是我们为会话生成的稳定键
        self.app_key = app_key
        self.app_info = app_info
        self.volume_controller = volume_controller
        self.config = config
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                padding: 10px;
                margin: 5px 0px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # 应用名称
        display_name = self.app_info.get('display_name') or self.app_info.get('name') or self.app_key
        app_label = QLabel(display_name)
        app_label.setFont(QFont('Arial', 11, QFont.Bold))
        app_label.setMinimumWidth(150)
        layout.addWidget(app_label)
        
        # 音量滑块
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setMinimumWidth(200)
        
        # 获取当前音量
        try:
            current_volume = self.volume_controller.get_app_volume(self.app_key)
            if current_volume is not None:
                self.volume_slider.setValue(int(current_volume))
            else:
                self.volume_slider.setValue(self.config.get('default_volume', 50))
        except:
            self.volume_slider.setValue(self.config.get('default_volume', 50))
        
        self.volume_slider.sliderMoved.connect(self.on_volume_changed)
        self.volume_slider.sliderPressed.connect(self.on_slider_pressed)
        self.volume_slider.sliderReleased.connect(self.on_slider_released)
        layout.addWidget(self.volume_slider)
        
        # 音量百分比显示
        self.volume_label = QLabel(f'{self.volume_slider.value()}%')
        self.volume_label.setMinimumWidth(40)
        self.volume_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.volume_label)
        
        # 重置按钮
        reset_btn = QPushButton('重置')
        reset_btn.setMaximumWidth(60)
        reset_btn.clicked.connect(self.reset_volume)
        layout.addWidget(reset_btn)
        
        # 静音按钮
        mute_btn = QPushButton('🔇 静音')
        mute_btn.setMaximumWidth(80)
        mute_btn.clicked.connect(self.toggle_mute)
        layout.addWidget(mute_btn)
    
    def on_volume_changed(self, value):
        """音量改变"""
        self.volume_label.setText(f'{value}%')
        self.update_app_volume(value)
    
    def on_slider_pressed(self):
        """滑块被按下"""
        pass
    
    def on_slider_released(self):
        """滑块释放"""
        self.update_app_volume(self.volume_slider.value())
    
    def update_app_volume(self, volume):
        """更新应用音量"""
        try:
            self.volume_controller.set_app_volume(self.app_key, volume)
        except Exception as e:
            print(f"设置 {self.app_key} 音量失败: {e}")
    
    def reset_volume(self):
        """重置音量"""
        default_volume = self.config.get('default_volume', 50)
        self.volume_slider.setValue(default_volume)
        self.update_app_volume(default_volume)
    
    def toggle_mute(self):
        """切换静音"""
        try:
            self.volume_controller.toggle_mute(self.app_key)
        except Exception as e:
            print(f"切换 {self.app_key} 静音失败: {e}")
