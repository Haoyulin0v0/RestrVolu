# 📁 项目文件结构说明

## 完整项目结构

```
Volume_Control/
│
├── 📄 main.py                    # 主应用入口
├── 📄 build.py                   # Python构建脚本
├── 📄 build.bat                  # Windows构建脚本
├── 📄 run.bat                    # Windows快速启动脚本
├── 📄 setup.py                   # pip安装配置
├── 📄 check_environment.py       # 环境检查脚本
├── 📄 test_core.py              # 单元测试
├── 📄 requirements.txt          # Python依赖列表
├── 📄 .gitignore                # Git忽略文件
│
├── 📚 文档文件
│   ├── README.md                # 完整使用文档
│   ├── QUICK_START.md           # 快速开始指南
│   ├── TROUBLESHOOTING.md       # 故障排除指南
│   ├── PROJECT_STRUCTURE.md     # 本文件
│   └── config.example.json      # 配置文件示例
│
├── 📁 core/                     # 核心功能模块
│   ├── __init__.py
│   ├── volume_controller.py     # 音量控制核心
│   ├── process_monitor.py       # 系统进程监听
│   └── advanced_features.py     # 高级功能（预设、定时等）
│
├── 📁 ui/                       # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py           # 主窗口UI
│   └── app_widget.py            # 应用音量小部件
│
├── 📁 dist/                     # 输出文件夹（构建后生成）
│   └── VolumeControl.exe        # 最终的可执行文件
│
└── 📁 build/                    # 构建中间文件（构建时生成）
    └── (various temporary files)
```

## 📄 文件说明

### 主要文件

| 文件名 | 说明 |
|------|------|
| `main.py` | 应用入口，处理配置加载和窗口创建 |
| `build.py` | Python脚本，使用PyInstaller打包EXE |
| `requirements.txt` | 项目依赖列表 |

### 快速启动文件

| 文件名 | 说明 |
|------|------|
| `run.bat` | 一键启动应用（自动安装依赖） |
| `build.bat` | 一键打包成EXE（自动安装PyInstaller） |

### 核心模块 (core/)

| 文件名 | 说明 |
|------|------|
| `volume_controller.py` | 使用pycaw控制应用音量 |
| `process_monitor.py` | 监听系统进程和音频应用 |
| `advanced_features.py` | 预设、配置文件、定时功能 |

### UI模块 (ui/)

| 文件名 | 说明 |
|------|------|
| `main_window.py` | 主窗口，包含标签页和布局 |
| `app_widget.py` | 单个应用的音量控制小部件 |

### 文档文件

| 文件名 | 说明 |
|------|------|
| `README.md` | 完整的项目文档 |
| `QUICK_START.md` | 30秒快速开始指南 |
| `TROUBLESHOOTING.md` | 常见问题和解决方案 |
| `config.example.json` | 配置文件示例 |

---

## 🔄 工作流程

### 用户工作流程

```
用户双击 VolumeControl.exe
    ↓
应用启动 (main.py)
    ↓
加载配置 (.volume_control/config.json)
    ↓
显示主窗口 (main_window.py)
    ↓
启动进程监听线程 (process_monitor.py)
    ↓
获取音频应用列表 → 显示应用小部件 (app_widget.py)
    ↓
用户调节音量 → 调用 volume_controller.py
    ↓
保存配置到 config.json
```

### 开发者工作流程

```
编辑源代码
    ↓
运行 python main.py 测试
    ↓
修改完成后运行 python build.py
    ↓
PyInstaller 打包源代码
    ↓
生成 dist/VolumeControl.exe
    ↓
用户运行 .exe 文件
```

---

## 🔧 模块间依赖关系

```
main.py
  ├── main_window.py
  │   ├── volume_controller.py
  │   ├── process_monitor.py
  │   └── app_widget.py
  │       └── volume_controller.py
  │
  └── config 管理
      └── config.json
```

---

## 💾 数据流

### 配置文件流

```
第一次运行
  → 创建 ~/.volume_control/ 目录
  → 生成默认 config.json
  
用户修改设置
  → 立即保存到 config.json
  
应用重启
  → 读取保存的 config.json
```

### 音量控制流

```
用户拖动滑块
  ↓
app_widget.py 捕获事件
  ↓
调用 volume_controller.set_app_volume()
  ↓
使用 pycaw 通过 Windows API 控制
  ↓
实时反映音量变化
```

---

## 🚀 启动方式

### 方式一：EXE（推荐用户使用）
```
双击 → dist/VolumeControl.exe
```

### 方式二：批处理脚本（用户）
```
双击 → run.bat
```

### 方式三：Python命令（开发者）
```
cmd → python main.py
```

### 方式四：虚拟环境（开发者）
```
cmd → venv\Scripts\activate
    → python main.py
```

---

## 📦 构建流程

```
build.bat 或 python build.py
  ↓
检查 PyInstaller 是否安装
  ↓
清理之前的构建文件
  ↓
PyInstaller 分析主脚本
  ↓
收集所有依赖
  ↓
生成 Windows 可执行文件
  ↓
输出 → dist/VolumeControl.exe
```

---

## 📝 配置文件位置

| 系统 | 路径 |
|------|------|
| Windows | `C:\Users\用户名\.volume_control\config.json` |
| 备用路径 | `%USERPROFILE%\.volume_control\config.json` |

---

## 🎯 关键代码位置

| 功能 | 文件位置 |
|------|---------|
| 音量控制 | `core/volume_controller.py` 行 ~15-60 |
| 进程监听 | `core/process_monitor.py` 行 ~20-40 |
| UI界面 | `ui/main_window.py` 行 ~50-150 |
| 设置界面 | `ui/main_window.py` 行 ~90-140 |
| 应用列表 | `ui/main_window.py` 行 ~75-90 |

---

## 🔐 文件权限

某些功能需要特定权限：
- ✓ 音量控制：需要系统权限（管理员）
- ✓ 进程读取：标准用户权限
- ✓ 配置读写：用户权限

建议以管理员身份运行以获得最佳体验。

---

**完成！现在你的项目结构已经完全建立。** ✓
