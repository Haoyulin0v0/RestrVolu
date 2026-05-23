"""
快速测试脚本 - 验证修复
"""

from comtypes import CoInitialize, CoUninitialize
from core.process_monitor import ProcessMonitor
from core.volume_controller import VolumeController

def test_app_detection():
    """测试应用检测"""
    print("=" * 60)
    print("测试应用检测...")
    print("=" * 60)
    print()
    
    CoInitialize()
    try:
        monitor = ProcessMonitor()
        apps = monitor.get_audio_apps()
        
        print(f"检测到 {len(apps)} 个音频应用:\n")
        
        for app_name, app_info in apps.items():
            print(f"✓ {app_name}")
            print(f"  PID: {app_info['pid']}")
            
        if len(apps) == 0:
            print("❌ 未检测到任何应用")
            print("\n请:")
            print("1. 打开浏览器")
            print("2. 播放YouTube视频")
            print("3. 重新运行此脚本")
        else:
            # 检查是否有 Apple Music
            apple_found = False
            for app_name in apps.keys():
                if 'apple' in app_name.lower() or 'music' in app_name.lower():
                    apple_found = True
                    print(f"\n✅ Apple Music 已检测到: {app_name}")
            
            if not apple_found:
                print("\n⚠️  未检测到 Apple Music")
                print("请检查 Apple Music 是否正在运行并播放音乐")
        
        print()
    finally:
        CoUninitialize()

def test_volume_control():
    """测试音量控制"""
    print("=" * 60)
    print("测试音量控制...")
    print("=" * 60)
    print()
    
    CoInitialize()
    try:
        controller = VolumeController()
        
        print(f"检测到 {len(controller.sessions)} 个音频会话")
        
        for app_name in controller.sessions.keys():
            try:
                volume = controller.get_app_volume(app_name)
                print(f"\n{app_name}: {volume}%")
            except Exception as e:
                print(f"\n{app_name}: [错误: {e}]")
        
        print()
    finally:
        CoUninitialize()

if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "🔊 快速测试 - 修复验证" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    test_app_detection()
    test_volume_control()
    
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print("\n")
