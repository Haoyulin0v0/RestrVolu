"""
系统进程监听模块
自动检测有音频输出的应用
"""

import psutil
from pycaw.pycaw import AudioUtilities

class ProcessMonitor:
    """进程监听器"""
    
    def __init__(self):
        self.exclude_processes = {
            'svchost.exe', 'system', 'wininit.exe', 'csrss.exe',
            'lsass.exe', 'services.exe', 'explorer.exe', 'dwm.exe',
            'audiodg.exe', 'conhost.exe', 'taskhostw.exe'
        }
    
    def _get_session_key(self, session):
        """生成稳定的音频会话唯一键"""
        process = session.Process
        app_name = process.name()
        group = getattr(session, 'GroupingParam', None)
        if group:
            return f"{app_name}::{process.pid}::{group}"
        return f"{app_name}::{process.pid}::{id(session)}"
    
    def get_audio_apps(self):
        """
        获取当前所有有音频输出的应用
        
        Returns:
            dict: {会话键: 应用信息}
        """
        audio_apps = {}
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process:
                    try:
                        process = session.Process
                        app_name = process.name()
                        app_name_lower = app_name.lower()
                        
                        # 跳过系统进程
                        if app_name_lower in self.exclude_processes:
                            continue
                        
                        # 检查是否是真实的应用进程
                        if self.is_valid_audio_app(process, app_name_lower):
                            session_key = self._get_session_key(session)
                            audio_apps[session_key] = {
                                'pid': process.pid,
                                'name': app_name,
                                'exe': process.exe(),
                                'group': str(getattr(session, 'GroupingParam', '')),
                                'display_name': getattr(session, 'DisplayName', ''),
                            }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            print(f"获取音频应用失败: {e}")
        
        return audio_apps
    
    def is_valid_audio_app(self, process, app_name_lower=None):
        """检查是否是有效的音频应用"""
        try:
            # 检查进程是否仍在运行
            try:
                if not process.is_running():
                    return False
            except:
                # 如果无法检查运行状态，假设它正在运行
                pass
            
            # 获取进程名
            if app_name_lower is None:
                app_name_lower = process.name().lower()
            
            # 排除一些系统进程
            exclude_names = {
                'system', 'svchost.exe', 'csrss.exe', 'lsass.exe',
                'services.exe', 'wininit.exe', 'explorer.exe', 'dwm.exe',
                'audiodg.exe', 'conhost.exe', 'taskhostw.exe', 'spoolsv.exe',
                'winlogon.exe', 'lsm.exe', 'wkssvc.exe', 'wuauserv.exe'
            }
            
            if app_name_lower in exclude_names:
                return False
            
            # 接受所有其他进程
            return True
        except Exception:
            # 如果检查失败，返回True，避免过滤掉有效应用
            return True
    
    def get_app_details(self, app_name):
        """获取应用详细信息"""
        try:
            for proc in psutil.process_iter(['name', 'exe', 'pid']):
                if proc.name() == app_name:
                    return {
                        'name': app_name,
                        'pid': proc.pid,
                        'exe': proc.exe(),
                    }
        except:
            pass
        return None
