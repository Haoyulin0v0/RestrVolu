"""
主窗口UI模块
"""

import sys
import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QScrollArea, QFrame, QCheckBox, QSpinBox,
    QTabWidget, QSystemTrayIcon, QMenu, QAction, QPlainTextEdit,
    QComboBox, QLineEdit, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap, QPainter
from comtypes import CoInitialize, CoUninitialize

from core.volume_controller import VolumeController
from core.process_monitor import ProcessMonitor
from ui.app_widget import AppWidget

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    keyboard = None
    KEYBOARD_AVAILABLE = False

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
        CoInitialize()
        try:
            monitor = ProcessMonitor()
            while self.running:
                try:
                    current_apps = monitor.get_audio_apps()
                    if current_apps != self.last_apps:
                        self.last_apps = current_apps
                        self.apps_updated.emit(current_apps)
                    self.msleep(1000)
                except Exception as e:
                    print(f"监听错误: {e}")
        finally:
            CoUninitialize()
    
    def stop(self):
        self.running = False

class HotkeyThread(QThread):
    """全局热键监听线程"""
    hotkey_triggered = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        if not KEYBOARD_AVAILABLE:
            return
        try:
            keyboard.add_hotkey('ctrl+shift+up', lambda: self.hotkey_triggered.emit('increase'))
            keyboard.add_hotkey('ctrl+shift+down', lambda: self.hotkey_triggered.emit('decrease'))
            keyboard.add_hotkey('ctrl+shift+m', lambda: self.hotkey_triggered.emit('mute'))
            while self.running:
                self.msleep(200)
        except Exception as e:
            print(f"热键监听失败: {e}")
        finally:
            try:
                keyboard.clear_all_hotkeys()
            except Exception:
                pass

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.volume_controller = VolumeController()
        self.monitor_thread = None
        self.hotkey_thread = None
        self.tray_icon = None
        self.app_widgets = {}
        self.selected_app_key = None
        self.quitting = False
        
        self.init_ui()
        self.setup_tray()
        self.setup_hotkeys()
        self.setup_monitoring()
        self.apply_theme(self.config.get('theme', 'light'))
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('🔊 音量控制工具')
        self.setGeometry(100, 100, 900, 650)
        self.setMinimumSize(700, 450)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel('🔊 系统音量控制')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        main_layout.addWidget(title)
        
        self.current_app_label = QLabel('当前选择应用: 无')
        self.current_app_label.setFont(QFont('Arial', 10))
        main_layout.addWidget(self.current_app_label)
        
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self.apps_tab = QWidget()
        self.apps_layout = QVBoxLayout(self.apps_tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.apps_scroll_layout = QVBoxLayout(scroll_widget)
        self.apps_scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        self.apps_layout.addWidget(scroll)
        
        self.tab_widget.addTab(self.apps_tab, '🎵 应用音量')
        
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_layout.addWidget(QLabel('默认应用音量 (%)'))
        default_vol_layout = QHBoxLayout()
        self.default_volume_spin = QSpinBox()
        self.default_volume_spin.setRange(0, 100)
        self.default_volume_spin.setValue(self.config.get('default_volume', 50))
        self.default_volume_spin.valueChanged.connect(self.on_default_volume_changed)
        default_vol_layout.addWidget(self.default_volume_spin)
        default_vol_layout.addStretch()
        settings_layout.addLayout(default_vol_layout)
        
        settings_layout.addSpacing(10)
        self.auto_control_checkbox = QCheckBox('启用自动音量控制')
        self.auto_control_checkbox.setChecked(self.config.get('auto_control_enabled', True))
        self.auto_control_checkbox.stateChanged.connect(self.on_auto_control_toggled)
        settings_layout.addWidget(self.auto_control_checkbox)
        
        settings_layout.addSpacing(10)
        settings_layout.addWidget(QLabel('应用过滤模式'))
        self.list_mode_combo = QComboBox()
        self.list_mode_combo.addItems(['黑名单模式', '白名单模式'])
        mode = self.config.get('list_mode', 'blacklist')
        self.list_mode_combo.setCurrentIndex(0 if mode == 'blacklist' else 1)
        self.list_mode_combo.currentIndexChanged.connect(self.on_list_mode_changed)
        settings_layout.addWidget(self.list_mode_combo)
        
        settings_layout.addSpacing(10)
        settings_layout.addWidget(QLabel('黑名单应用 (每行一个)'))
        self.blacklist_edit = QPlainTextEdit()
        self.blacklist_edit.setPlaceholderText('例如: chrome.exe\nspotify.exe')
        self.blacklist_edit.setFixedHeight(90)
        self.blacklist_edit.setPlainText('\n'.join(self.config.get('blacklisted_apps', [])))
        self.blacklist_edit.textChanged.connect(self.on_blacklist_changed)
        settings_layout.addWidget(self.blacklist_edit)
        
        settings_layout.addSpacing(10)
        settings_layout.addWidget(QLabel('白名单应用 (每行一个)'))
        self.whitelist_edit = QPlainTextEdit()
        self.whitelist_edit.setPlaceholderText('例如: zoom.exe\nvlc.exe')
        self.whitelist_edit.setFixedHeight(90)
        self.whitelist_edit.setPlainText('\n'.join(self.config.get('whitelisted_apps', [])))
        self.whitelist_edit.textChanged.connect(self.on_whitelist_changed)
        settings_layout.addWidget(self.whitelist_edit)
        
        settings_layout.addSpacing(10)
        settings_layout.addWidget(QLabel('主题'))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['light', 'dark'])
        self.theme_combo.setCurrentText(self.config.get('theme', 'light'))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        settings_layout.addWidget(self.theme_combo)
        
        settings_layout.addSpacing(10)
        settings_layout.addWidget(QLabel('音量预设'))
        preset_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        preset_layout.addWidget(self.preset_combo)
        self.apply_preset_btn = QPushButton('应用预设')
        self.apply_preset_btn.clicked.connect(self.on_preset_apply)
        preset_layout.addWidget(self.apply_preset_btn)
        self.remove_preset_btn = QPushButton('删除预设')
        self.remove_preset_btn.clicked.connect(self.on_preset_remove)
        preset_layout.addWidget(self.remove_preset_btn)
        settings_layout.addLayout(preset_layout)
        
        save_layout = QHBoxLayout()
        self.preset_name_input = QLineEdit()
        self.preset_name_input.setPlaceholderText('预设名称')
        save_layout.addWidget(self.preset_name_input)
        self.save_preset_btn = QPushButton('保存当前')
        self.save_preset_btn.clicked.connect(self.on_preset_save)
        save_layout.addWidget(self.save_preset_btn)
        settings_layout.addLayout(save_layout)
        
        settings_layout.addSpacing(10)
        help_text = QLabel(
            '💡 提示:\n'
            '• 黑名单模式下，列出的应用将不参与自动控制\n'
            '• 白名单模式下，仅列出的应用会被自动控制\n'
            '• 预设可保存当前可见应用的音量设置\n'
            '• 热键 Ctrl+Shift+Up/Down 控制选择应用音量，Ctrl+Shift+M 切换静音'
        )
        help_text.setFont(QFont('Arial', 9))
        help_text.setStyleSheet('color: #666; line-height: 1.5;')
        settings_layout.addWidget(help_text)
        
        settings_layout.addStretch()
        self.tab_widget.addTab(settings_tab, '⚙️ 设置')
        self.refresh_preset_dropdown()
    
    def setup_monitoring(self):
        """设置进程监听"""
        self.monitor_thread = ProcessMonitorThread(self.volume_controller)
        self.monitor_thread.apps_updated.connect(self.update_app_widgets)
        self.monitor_thread.start()
    
    def setup_hotkeys(self):
        """设置热键监听"""
        self.hotkey_thread = HotkeyThread()
        self.hotkey_thread.hotkey_triggered.connect(self.on_hotkey_event)
        if KEYBOARD_AVAILABLE:
            self.hotkey_thread.start()
        else:
            print('keyboard 模块未安装，热键功能不可用。')
    
    def setup_tray(self):
        """设置系统托盘"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            icon = QIcon(self.create_tray_pixmap())
            self.tray_icon = QSystemTrayIcon(icon, self)
            self.tray_icon.setToolTip('音量控制工具')
            tray_menu = QMenu()
            show_action = QAction('显示主窗口', self)
            show_action.triggered.connect(self.show_main_window)
            tray_menu.addAction(show_action)
            exit_action = QAction('退出', self)
            exit_action.triggered.connect(self.quit_app)
            tray_menu.addAction(exit_action)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.on_tray_activated)
            self.tray_icon.show()
    
    def create_tray_pixmap(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor('#4CAF50'))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.setBrush(QColor('white'))
        painter.drawRect(28, 20, 8, 24)
        painter.drawRect(20, 36, 24, 8)
        painter.end()
        return pixmap
    
    def update_app_widgets(self, apps):
        """更新应用列表"""
        for app_key in list(self.app_widgets.keys()):
            if app_key not in apps:
                widget = self.app_widgets[app_key]
                self.apps_scroll_layout.removeWidget(widget)
                widget.deleteLater()
                del self.app_widgets[app_key]
                if self.selected_app_key == app_key:
                    self.selected_app_key = None
        
        for app_key, app_info in apps.items():
            auto_allowed = self.is_auto_control_app(app_info)
            if app_key not in self.app_widgets:
                widget = AppWidget(
                    app_key, app_info, self.volume_controller, self.config,
                    is_auto_controlled=auto_allowed,
                    select_callback=self.select_app,
                    selected=(self.selected_app_key == app_key)
                )
                index = self.apps_scroll_layout.count() - 1
                self.apps_scroll_layout.insertWidget(index, widget)
                self.app_widgets[app_key] = widget
                if self.selected_app_key is None:
                    self.select_app(app_key)
                if self.config.get('auto_control_enabled', True) and auto_allowed:
                    try:
                        default_vol = self.config.get('default_volume', 50)
                        self.volume_controller.set_app_mute(app_key, True)
                        self.volume_controller.set_app_volume(app_key, default_vol)
                        QTimer.singleShot(250, lambda key=app_key: self.volume_controller.set_app_mute(key, False))
                    except Exception as e:
                        print(f"自动设置默认音量失败 ({app_key}): {e}")

        self.update_current_app_label()
    
    def select_app(self, app_key):
        if self.selected_app_key == app_key:
            return
        self.selected_app_key = app_key
        for key, widget in self.app_widgets.items():
            widget.set_selected(key == app_key)
        self.update_current_app_label()
    
    def update_current_app_label(self):
        if self.selected_app_key and self.selected_app_key in self.app_widgets:
            info = self.app_widgets[self.selected_app_key].app_info
            name = info.get('display_name') or info.get('name') or self.selected_app_key
            self.current_app_label.setText(f'当前选择应用: {name}')
        else:
            self.current_app_label.setText('当前选择应用: 无')
    
    def on_default_volume_changed(self, value):
        self.config['default_volume'] = value
        self.save_config()
    
    def on_auto_control_toggled(self, state):
        self.config['auto_control_enabled'] = state == Qt.Checked
        self.save_config()
    
    def on_list_mode_changed(self, index):
        self.config['list_mode'] = 'blacklist' if index == 0 else 'whitelist'
        self.save_config()
        self.update_widget_auto_states()
    
    def on_blacklist_changed(self):
        self.config['blacklisted_apps'] = self.parse_app_list(self.blacklist_edit.toPlainText())
        self.save_config()
        self.update_widget_auto_states()
    
    def on_whitelist_changed(self):
        self.config['whitelisted_apps'] = self.parse_app_list(self.whitelist_edit.toPlainText())
        self.save_config()
        self.update_widget_auto_states()
    
    def on_theme_changed(self, theme):
        self.config['theme'] = theme
        self.save_config()
        self.apply_theme(theme)
    
    def on_preset_save(self):
        name = self.preset_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '请输入预设名称。')
            return
        volumes = {
            key: widget.volume_slider.value()
            for key, widget in self.app_widgets.items()
        }
        self.config.setdefault('presets', {})[name] = volumes
        self.save_config()
        self.refresh_preset_dropdown()
        QMessageBox.information(self, '成功', f'已保存预设：{name}')
    
    def on_preset_apply(self):
        name = self.preset_combo.currentText()
        presets = self.config.get('presets', {})
        if not name or name not in presets:
            QMessageBox.warning(self, '提示', '请选择有效的预设。')
            return
        preset = presets[name]
        for key, volume in preset.items():
            widget = self.app_widgets.get(key)
            if widget:
                widget.set_volume(volume)
        QMessageBox.information(self, '成功', f'已应用预设：{name}')
    
    def on_preset_remove(self):
        name = self.preset_combo.currentText()
        if not name:
            QMessageBox.warning(self, '提示', '请选择要删除的预设。')
            return
        presets = self.config.get('presets', {})
        if name in presets:
            del presets[name]
            self.save_config()
            self.refresh_preset_dropdown()
            QMessageBox.information(self, '成功', f'已删除预设：{name}')
    
    def refresh_preset_dropdown(self):
        self.preset_combo.clear()
        presets = self.config.get('presets', {}) or {}
        if presets:
            self.preset_combo.addItems(sorted(presets.keys()))
        else:
            self.preset_combo.addItem('无预设')
    
    def parse_app_list(self, content):
        return [line.strip() for line in content.splitlines() if line.strip()]
    
    def update_widget_auto_states(self):
        for widget in self.app_widgets.values():
            widget.update_auto_control_state(self.is_auto_control_app(widget.app_info))
    
    def is_auto_control_app(self, app_info):
        name = (app_info.get('name') or '').lower()
        if not name:
            return True
        if self.config.get('list_mode', 'blacklist') == 'blacklist':
            return name not in [item.lower() for item in self.config.get('blacklisted_apps', [])]
        whitelist = [item.lower() for item in self.config.get('whitelisted_apps', [])]
        return name in whitelist if whitelist else True
    
    def on_hotkey_event(self, action):
        if action == 'increase':
            self.adjust_selected_app_volume(5)
        elif action == 'decrease':
            self.adjust_selected_app_volume(-5)
        elif action == 'mute':
            self.toggle_selected_app_mute()
    
    def adjust_selected_app_volume(self, delta):
        widget = self.app_widgets.get(self.selected_app_key)
        if widget:
            new_value = max(0, min(100, widget.volume_slider.value() + delta))
            widget.set_volume(new_value)
        else:
            current = self.volume_controller.get_system_volume()
            if current is not None:
                self.volume_controller.set_system_volume(max(0, min(100, current + delta)))
    
    def toggle_selected_app_mute(self):
        widget = self.app_widgets.get(self.selected_app_key)
        if widget:
            widget.toggle_mute()
        else:
            self.volume_controller.set_system_volume(0)
    
    def save_config(self):
        from main import save_config
        save_config(self.config)
    
    def apply_theme(self, theme):
        if theme == 'dark':
            self.setStyleSheet(self.get_stylesheet(dark=True))
        else:
            self.setStyleSheet(self.get_stylesheet(dark=False))
    
    def get_stylesheet(self, dark=False):
        if dark:
            return """
                QMainWindow { background-color: #2b2b2b; }
                QLabel { color: #f0f0f0; }
                QPushButton { background-color: #5c9c4f; color: white; }
                QPushButton:hover { background-color: #6bbf64; }
                QPushButton:pressed { background-color: #4f8c40; }
                QSlider::groove:horizontal { background-color: #555; }
                QSlider::handle:horizontal { background-color: #5c9c4f; }
                QScrollArea { border: none; background-color: #333; }
                QFrame { background-color: #3a3a3a; border: 1px solid #555; }
                QTabWidget::pane { border: 1px solid #555; }
                QTabBar::tab { background-color: #444; color: #f0f0f0; }
                QTabBar::tab:selected { background-color: #2b2b2b; }
                QSpinBox, QLineEdit, QPlainTextEdit { background-color: #2e2e2e; color: #f0f0f0; border: 1px solid #555; }
                QCheckBox { color: #f0f0f0; }
                QCheckBox::indicator:unchecked { background-color: #2e2e2e; border: 1px solid #777; }
                QCheckBox::indicator:checked { background-color: #5c9c4f; border: 1px solid #5c9c4f; }
            """
        return """
            QMainWindow { background-color: #f5f5f5; }
            QLabel { color: #333; }
            QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
            QSlider::groove:horizontal { background-color: #e0e0e0; height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background-color: #4CAF50; width: 18px; margin: -5px 0; border-radius: 9px; }
            QSlider::handle:horizontal:hover { background-color: #45a049; }
            QScrollArea { border: none; background-color: white; }
            QFrame { background-color: white; border-radius: 4px; border: 1px solid #e0e0e0; }
            QTabWidget::pane { border: 1px solid #e0e0e0; }
            QTabBar::tab { background-color: #e0e0e0; padding: 6px 20px; }
            QTabBar::tab:selected { background-color: white; }
            QSpinBox, QLineEdit, QPlainTextEdit { border: 1px solid #ddd; border-radius: 4px; padding: 4px; }
            QCheckBox { spacing: 5px; }
            QCheckBox::indicator:unchecked { background-color: white; border: 1px solid #ddd; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #4CAF50; border: 1px solid #4CAF50; border-radius: 3px; }
        """
    
    def show_main_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_main_window()
    
    def quit_app(self):
        self.quitting = True
        self.stop_threads()
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.instance().quit()
    
    def stop_threads(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        if self.hotkey_thread:
            self.hotkey_thread.stop()
            self.hotkey_thread.wait()
    
    def closeEvent(self, event):
        if not self.quitting and self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage('音量控制工具', '程序已最小化到系统托盘。双击图标或右键菜单恢复。', QSystemTrayIcon.Information, 3000)
            event.ignore()
            return
        self.stop_threads()
        event.accept()
