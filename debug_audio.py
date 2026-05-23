"""
调试脚本 - 检查音频应用和COM问题
用来诊断为什么某些应用（如Apple Music）不显示
"""

import sys
from comtypes import CoInitialize, CoUninitialize

def check_audio_sessions():
    """检查所有音频会话"""
    print("=" * 60)
    print("正在检查系统中的所有音频应用...")
    print("=" * 60)
    
    try:
        CoInitialize()
        try:
            from pycaw.pycaw import AudioUtilities
            
            sessions = AudioUtilities.GetAllSessions()
            print(f"\n找到 {len(list(sessions))} 个音频会话\n")
            
            # 重新获取会话列表（因为迭代器已用完）
            sessions = AudioUtilities.GetAllSessions()
            app_count = 0
            
            for session in sessions:
                if session.Process:
                    try:
                        app_count += 1
                        process = session.Process
                        print(f"应用 {app_count}:")
                        print(f"  进程名: {process.name()}")
                        print(f"  PID: {process.pid}")
                        try:
                            print(f"  路径: {process.exe()}")
                        except:
                            print(f"  路径: [无法获取]")
                        
                        # 尝试获取音量
                        try:
                            volume = session.SimpleAudioVolume
                            current_volume = volume.GetMasterVolume()
                            print(f"  当前音量: {int(current_volume * 100)}%")
                        except:
                            print(f"  当前音量: [无法获取]")
                        print()
                    except Exception as e:
                        print(f"  [错误获取应用信息: {e}]\n")
            
            if app_count == 0:
                print("❌ 未找到任何音频应用")
                print("\n提示:")
                print("1. 请打开浏览器并播放YouTube视频")
                print("2. 或打开音乐播放器应用")
                print("3. 然后重新运行此脚本")
            else:
                print(f"✅ 找到 {app_count} 个音频应用\n")
                
        finally:
            CoUninitialize()
            
    except Exception as e:
        print(f"❌ 检查音频会话失败: {e}")
        import traceback
        traceback.print_exc()


def check_apple_music():
    """检查Apple Music进程"""
    print("=" * 60)
    print("正在检查Apple Music进程...")
    print("=" * 60)
    
    try:
        import psutil
        
        apple_music_found = False
        
        for proc in psutil.process_iter(['name', 'exe', 'pid']):
            try:
                name_lower = proc.name().lower()
                if 'apple' in name_lower or 'music' in name_lower:
                    apple_music_found = True
                    print(f"\n找到Apple相关进程:")
                    print(f"  进程名: {proc.name()}")
                    print(f"  PID: {proc.pid}")
                    try:
                        print(f"  路径: {proc.exe()}")
                    except:
                        print(f"  路径: [无法获取]")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not apple_music_found:
            print("\n❌ 未找到Apple Music进程")
            print("\n可能的原因:")
            print("1. Apple Music 未运行")
            print("2. Apple Music 正在浏览器中运行 (Web版本)")
            print("3. Apple Music 的进程名不同")
            print("\n请:")
            print("1. 打开 Apple Music 应用或网页版")
            print("2. 播放一首歌曲")
            print("3. 重新运行此脚本")
        else:
            print("\n✅ 找到Apple Music进程")
            print("\n现在检查是否生成了音频会话...")
            
            # 再次检查音频会话
            CoInitialize()
            try:
                from pycaw.pycaw import AudioUtilities
                
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    if session.Process:
                        if 'apple' in session.Process.name().lower() or \
                           'music' in session.Process.name().lower():
                            print(f"✅ Apple Music 的音频会话已找到!")
                            print(f"   应用: {session.Process.name()}")
                            return
                
                print("⚠️  Apple Music 进程存在，但未生成音频会话")
                print("\n解决方案:")
                print("1. 在 Apple Music 中播放一首歌曲")
                print("2. 确保音量不是 0%")
                print("3. 重启 Apple Music")
                
            finally:
                CoUninitialize()
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主检查函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "🔊 音量控制工具 - 调试脚本" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    # 检查音频会话
    check_audio_sessions()
    
    print("\n")
    
    # 检查Apple Music
    check_apple_music()
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
    print("\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
