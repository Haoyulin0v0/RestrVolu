# 🔧 COM 初始化错误修复 - 说明文档

## 🎯 问题修复总结

已修复 Windows COM 库初始化错误：`[WinError -2147221008] 尚未调用 CoInitialize`

## ✅ 修复内容

### 1. COM 库初始化
- ✅ 在主线程中添加 `CoInitialize()` 和 `CoUninitialize()`
- ✅ 在监听线程 `ProcessMonitorThread` 中初始化 COM
- ✅ 确保主线程和监听线程都正确初始化 COM

### 2. 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `main.py` | 主线程中初始化/清理 COM |
| `ui/main_window.py` | 监听线程中初始化/清理 COM |
| `core/volume_controller.py` | 移除重复的 COM 初始化 |
| `core/process_monitor.py` | 移除重复的 COM 初始化 |

### 3. 工作流程

```
应用启动
  ↓
主线程: CoInitialize()
  ↓
创建监听线程
  ↓
监听线程: CoInitialize()
  ↓
获取音频应用 (现在正常工作)
  ↓
调整音量 (现在正常工作)
  ↓
应用关闭
  ↓
线程: CoUninitialize()
主线程: CoUninitialize()
```

---

## 📱 关于 Apple Music 的问题

### 可能的原因

1. **Apple Music 不支持独立音量控制**
   - 某些应用（如 Spotify 网页版）可能不支持 Windows 的独立音量控制
   - 这是应用本身的限制，不是工具的问题

2. **Apple Music 进程被过滤**
   - 检查进程名称是否在黑名单中
   - 可能需要手动添加到允许列表

3. **Apple Music 没有生成音频会话**
   - 某些应用可能使用特殊的音频输出方式
   - 可能需要重启应用或检查音频驱动

### 🔍 调试步骤

#### 步骤 1：检查 Apple Music 进程名

```python
import psutil

# 查找所有包含 "apple" 的进程
for proc in psutil.process_iter(['name', 'exe']):
    if 'apple' in proc.name().lower() or 'music' in proc.name().lower():
        print(f"进程名: {proc.name()}")
        print(f"可执行文件: {proc.exe()}")
```

#### 步骤 2：检查是否生成音频会话

```python
from pycaw.pycaw import AudioUtilities

# 列出所有活跃的音频会话
for session in AudioUtilities.GetAllSessions():
    if session.Process:
        print(f"应用: {session.Process.name()}")
```

#### 步骤 3：手动测试音量控制

1. 打开 Apple Music 并播放音乐
2. 运行上面的 Python 代码
3. 检查是否看到 Apple Music 的进程

### ✅ 解决方案

#### 方案 1：从黑名单中移除（如果被过滤）

编辑 `core/process_monitor.py`：

```python
self.exclude_processes = {
    'svchost.exe', 'system', 'wininit.exe', 'csrss.exe',
    'lsass.exe', 'services.exe', 'explorer.exe', 'dwm.exe',
    'audiodg.exe', 'conhost.exe', 'taskhostw.exe'
    # 移除: # 'AppleMusic.exe' (如果之前被过滤)
}
```

#### 方案 2：检查 Apple Music 是否使用 Web 技术

如果 Apple Music 是网页应用，它可能在浏览器中运行：
- 试试控制浏览器（Chrome、Edge）的音量
- Apple Music 的音量可能与浏览器绑定

#### 方案 3：更新音频驱动

- 右键点击 "此电脑" → 属性
- 点击 "设备管理器"
- 展开 "声音、视频和游戏控制器"
- 右键音频设备 → 更新驱动程序

#### 方案 4：重启 Apple Music

有时候重启应用可以帮助重新生成音频会话：

```
1. 完全关闭 Apple Music
2. 等待 2-3 秒
3. 重新打开 Apple Music
4. 重新启动音量控制工具
```

---

## 🧪 测试 COM 修复

运行以下命令测试修复是否有效：

```bash
python check_environment.py
# 应该看到所有项都是 ✓
```

---

## 📝 相关文件位置

| 文件 | 位置 |
|------|------|
| 主程序 | `main.py` |
| 主窗口 | `ui/main_window.py` |
| 音量控制 | `core/volume_controller.py` |
| 进程监听 | `core/process_monitor.py` |

---

## 💡 如果问题仍然存在

### 1. 以管理员身份运行
```
右键 → 以管理员身份运行
```

### 2. 检查系统音量
- 右下角是否有音量图标
- 系统音量是否大于 0%

### 3. 查看错误日志
- 应用会在控制台打印错误信息
- 截图或复制错误信息进行诊断

### 4. 尝试其他应用
- 打开浏览器 (Chrome/Firefox/Edge)
- 播放 YouTube 视频
- 查看是否能看到浏览器在列表中

---

## ✨ 预期行为

修复后，应该能够：

✅ 看到所有正在播放音频的应用  
✅ 实时调节每个应用的音量  
✅ 快速静音应用  
✅ 没有 COM 错误信息  
✅ 新应用自动显示在列表中  

---

## 🎉 完成！

COM 初始化问题已修复。如果 Apple Music 仍然没有出现，请按照上面的调试步骤进行检查。

大多数情况下，Apple Music 可能：
- 正在浏览器中运行（检查浏览器）
- 不支持独立音量控制（这不是工具的问题）
- 需要重启才能生成音频会话
