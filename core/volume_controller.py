"""
音量控制核心模块
使用 pycaw 库控制Windows应用音量
"""

from ctypes import *
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

class VolumeController:
    """音量控制器"""
    
    def __init__(self):
        self.sessions = {}
        self.refresh_sessions()
    
    def _get_session_key(self, session):
        """生成稳定的音频会话唯一键"""
        process = session.Process
        app_name = process.name()
        group = getattr(session, 'GroupingParam', None)
        if group:
            return f"{app_name}::{process.pid}::{group}"
        return f"{app_name}::{process.pid}::{id(session)}"
    
    def refresh_sessions(self):
        """刷新所有音频会话"""
        try:
            self.sessions = {}
            # 获取所有活跃的音频会话
            for session in AudioUtilities.GetAllSessions():
                if session.Process:
                    try:
                        session_key = self._get_session_key(session)
                        self.sessions[session_key] = session
                    except:
                        pass
        except Exception as e:
            print(f"刷新会话失败: {e}")
    
    def get_app_volume(self, app_key):
        """获取应用当前音量"""
        try:
            self.refresh_sessions()
            if app_key in self.sessions:
                session = self.sessions[app_key]
                volume = session.SimpleAudioVolume
                return int(volume.GetMasterVolume() * 100)
        except Exception as e:
            print(f"获取 {app_key} 音量失败: {e}")
        return None
    
    def set_app_volume(self, app_key, volume_percent):
        """
        设置应用音量
        
        Args:
            app_key: 应用会话键
            volume_percent: 音量百分比 (0-100)
        """
        try:
            self.refresh_sessions()
            if app_key in self.sessions:
                session = self.sessions[app_key]
                volume = session.SimpleAudioVolume
                # 转换为 0.0-1.0 范围
                volume_value = max(0, min(100, volume_percent)) / 100.0
                volume.SetMasterVolume(volume_value, None)
                return True
        except Exception as e:
            print(f"设置 {app_key} 音量失败: {e}")
        return False
    
    def toggle_mute(self, app_key):
        """切换应用静音"""
        try:
            self.refresh_sessions()
            if app_key in self.sessions:
                session = self.sessions[app_key]
                volume = session.SimpleAudioVolume
                current_mute = volume.GetMute()
                volume.SetMute(not current_mute, None)
                return True
        except Exception as e:
            print(f"切换 {app_key} 静音失败: {e}")
        return False

    def set_app_mute(self, app_key, mute=True):
        """设置应用静音状态

        Args:
            app_key: 会话键
            mute: True 为静音, False 为取消静音
        """
        try:
            self.refresh_sessions()
            if app_key in self.sessions:
                session = self.sessions[app_key]
                volume = session.SimpleAudioVolume
                volume.SetMute(bool(mute), None)
                return True
        except Exception as e:
            print(f"设置 {app_key} 静音状态失败: {e}")
        return False
    
    def get_system_volume(self):
        """获取系统音量"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            return int(volume.GetMasterVolumeLevelScalar() * 100)
        except Exception as e:
            print(f"获取系统音量失败: {e}")
        return None
    
    def set_system_volume(self, volume_percent):
        """设置系统音量"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume_value = max(0, min(100, volume_percent)) / 100.0
            volume.SetMasterVolumeLevelScalar(volume_value, None)
            return True
        except Exception as e:
            print(f"设置系统音量失败: {e}")
        return False
