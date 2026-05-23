"""
高级功能模块 - 自动化和预设
"""

import json
from pathlib import Path
from datetime import datetime

class AutoVolumeManager:
    """自动音量管理器"""
    
    def __init__(self, volume_controller, config):
        self.volume_controller = volume_controller
        self.config = config
        self.app_volumes = {}
    
    def auto_control_new_app(self, app_name):
        """自动控制新打开的应用"""
        if not self.config.get('auto_control_enabled', True):
            return False
        
        try:
            default_volume = self.config.get('default_volume', 50)
            # app_name 在新设计中是会话键 (app_key)
            self.volume_controller.set_app_volume(app_name, default_volume)
            
            # 记录到配置
            self.app_volumes[app_name] = default_volume
            return True
        except Exception as e:
            print(f"自动控制 {app_name} 失败: {e}")
            return False
    
    def get_volume_preset(self, preset_name):
        """获取音量预设"""
        presets = self.config.get('presets', {})
        return presets.get(preset_name)
    
    def apply_preset(self, preset_name, apps):
        """应用预设到指定的应用"""
        preset = self.get_volume_preset(preset_name)
        if not preset:
            return False
        
        for app_name in apps:
            volume = preset.get('default_volume', 50)
            # 传入的 app_name 应当为会话键 (app_key)
            self.volume_controller.set_app_volume(app_name, volume)
        
        return True
    
    def save_app_volume(self, app_name, volume):
        """保存应用的音量"""
        # 使用会话键进行保存
        self.app_volumes[app_name] = volume


class VolumeProfile:
    """音量配置文件管理"""
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path.home() / '.volume_control'
        self.config_dir = Path(config_dir)
        self.profiles_dir = self.config_dir / 'profiles'
        self.ensure_dirs()
    
    def ensure_dirs(self):
        """确保目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def save_profile(self, profile_name, app_volumes):
        """保存音量配置文件"""
        profile_data = {
            'name': profile_name,
            'created': datetime.now().isoformat(),
            'volumes': app_volumes
        }
        
        profile_file = self.profiles_dir / f'{profile_name}.json'
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        return str(profile_file)
    
    def load_profile(self, profile_name):
        """加载音量配置文件"""
        profile_file = self.profiles_dir / f'{profile_name}.json'
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_profiles(self):
        """列出所有配置文件"""
        profiles = []
        if self.profiles_dir.exists():
            for profile_file in self.profiles_dir.glob('*.json'):
                profiles.append(profile_file.stem)
        return profiles
    
    def delete_profile(self, profile_name):
        """删除配置文件"""
        profile_file = self.profiles_dir / f'{profile_name}.json'
        if profile_file.exists():
            profile_file.unlink()
            return True
        return False


class ScheduledVolumeControl:
    """定时音量控制"""
    
    def __init__(self, volume_controller):
        self.volume_controller = volume_controller
        self.schedules = []
    
    def add_schedule(self, app_name, time, volume):
        """添加定时规则
        
        Args:
            app_name: 应用名称
            time: 时间 (HH:MM格式)
            volume: 目标音量
        """
        # 存储为会话键 (app_key)
        schedule = {
            'app': app_name,
            'time': time,
            'volume': volume
        }
        self.schedules.append(schedule)
    
    def check_and_apply(self):
        """检查并应用定时规则"""
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M')
        
        for schedule in self.schedules:
            if schedule['time'] == current_time:
                try:
                    self.volume_controller.set_app_volume(
                        schedule['app'],
                        schedule['volume']
                    )
                except:
                    pass
