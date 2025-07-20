# C-Cleaner: 一款智能、安全的 Windows 大文件清理工具

一个为 Windows 用户设计的命令行工具，旨在安全、高效地扫描指定驱动器或目录，帮助您快速定位并清理占用空间的大文件。

## ✨ 功能特性

- **🎯 精准扫描**: 支持扫描任意驱动器（`C:\`, `D:\`）或特定文件夹（`C:\Users\YourUser\Downloads`）。
- **自定义筛选**: 您可以指定要查找的文件最小体积（如 `1GB`, `200MB`），并控制结果列表的长度。
- **🛡️ 智能安全排除**:
    - **自动防护**: 默认跳过所有关键系统目录 (`Windows`, `Program Files`)、用户数据目录及隐藏/系统文件，从根源上防止误删。
    - **持久化配置 (推荐)**: 通过 `.cleaner_ignore` 文件，您可以像使用 `.gitignore` 一样，永久性地排除您的游戏库、工作目录等。
    - **临时排除**: 使用 `--exclude` 参数，在单次运行时临时跳过指定目录。
- **清晰展示**: 结果以整洁的表格形式呈现，按文件大小降序排列，体积单位自动格式化。
- **安全删除**: 提供交互式确认，删除操作会将文件**移至回收站**，而不是永久删除，给您一个“后悔”的机会。
- **日志记录**: 详细的运行日志将记录在 `c_cleaner.log` 文件中，方便问题排查和操作审计。
- **纯命令行**: 无需图形界面，轻量、快速，适合开发者和高级用户。

## 🚀 安装与运行

### 1. 环境准备

- 确保您已安装 Python 3.6+。
- 安装所需的依赖库：
  ```bash
  pip install -r requirements.txt
  ```

### 2. 运行

打开命令行（CMD 或 PowerShell），进入项目目录，然后运行：

```bash
# 扫描 C 盘 (使用默认设置: 查找 >50MB 的文件, 显示前 20 个)
python c_cleaner.py

# 扫描 D 盘的特定目录，并自定义参数
python c_cleaner.py D:\Cache --min-size 500MB --top 10

# 支持的单位: B, KB, MB, GB, TB
python c_cleaner.py --min-size 1.5GB
```

### 排除目录

有两种方式可以排除您不想扫描的目录：

#### 方式一 (推荐): 使用 `.cleaner_ignore` 配置文件

在工具的运行目录下创建一个名为 `.cleaner_ignore` 的文本文件。将您想忽略的目录路径逐行写入，就像 `.gitignore` 一样。程序运行时会自动加载。

```ini
# .cleaner_ignore 文件示例
# 我的游戏库
D:\WeGameApps
D:\My Games\Steam

# 工作项目
C:\Users\YourUser\Documents\Projects
```

**2. 使用 `--exclude` 命令行参数 (用于临时排除)**

python c_cleaner.py D:\ --exclude D:\WeGameApp "D:\My Games\Steam"
```

## 📦 打包为 .exe (可选)

如果您想在没有安装 Python 的电脑上使用本工具，可以将其打包成一个独立的 `.exe` 文件。

1.  安装 PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  执行打包命令:
    ```bash
    pyinstaller --onefile --name c-cleaner c_cleaner.py
    ```
3.  打包完成后，您可以在生成的 `dist` 文件夹中找到 `c-cleaner.exe` 文件。