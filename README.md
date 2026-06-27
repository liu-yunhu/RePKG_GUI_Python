# RePKG-GUI Python Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Based on](https://img.shields.io/badge/Based%20on-RePKG-red.svg)](https://github.com/notscuffed/RePKG)

基于 [RePKG](https://github.com/notscuffed/RePKG) 命令行工具的图形界面包装器，使用 Python + tkinter 开发，支持文件拖放，用于解包 Steam Wallpaper Engine 壁纸文件。

## 功能特性

- **解包 PKG 文件**: 提取壁纸引擎的 PKG 资源包
- **转换 TEX 文件**: 将壁纸引擎的 TEX 纹理文件转换为 PNG 图片
- **查看信息**: 显示 PKG/TEX 文件的详细信息
- **文件拖放**: 支持直接拖放文件到程序中
- **批量处理**: 支持递归搜索子目录，批量处理多个文件
- **一键打开**: 解包完成后可直接打开输出目录

## 截图

```
+-----------------------------------------------+
|  RePKG-GUI Python Edition                    [X] |
+-----------------------------------------------+
|  [解包 PKG]  [查看信息]                          |
+-----------------------------------------------+
|  输入 (支持拖放):                                |
|  [PKG文件路径________________] [浏览...]        |
|                                                |
|  输出 (支持拖放):                                |
|  [输出目录路径______________] [浏览...]         |
|                                                |
|  选项:                                          |
|  [√] 递归搜索  [√] 复制项目文件  [√] 使用项目名称 |
|                                                |
|  [开始解包]              [打开输出目录]          |
|                                                |
|  日志输出:                                       |
|  > 开始解包...                                   |
|  > 解包完成!                                     |
+-----------------------------------------------+
```

## 系统要求

- Python 3.6 或更高版本
- Windows 操作系统 (已测试)
- tkinterdnd2 (可选，用于拖放功能)

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/your-username/RePKG-GUI-Python.git
cd RePKG-GUI-Python
```

2. 安装拖放支持 (可选)：
```bash
pip install tkinterdnd2
```

3. 确保 `RePKG.exe` 文件在程序目录下 (可从 [RePKG Releases](https://github.com/notscuffed/RePKG/releases) 下载)

## 使用方法

1. 运行程序：
```bash
python repkg_gui.py
```

2. 拖放 PKG/TEX 文件到输入框，或点击"浏览"选择文件
3. 确认输出目录 (默认为输入文件所在目录的 `output` 文件夹)
4. 配置选项后点击"开始解包"
5. 解包完成后可点击"打开输出目录"查看结果

## 命令行选项

| 选项 | 说明 |
|------|------|
| 递归搜索子目录 | 搜索所有子文件夹中的 PKG/TEX 文件 |
| 复制项目文件 | 复制 project.json 和预览图 |
| 使用项目名称 | 使用 project.json 中的标题作为输出目录名 |
| 单目录输出 | 所有文件输出到同一目录 |
| 覆盖已有文件 | 覆盖已存在的输出文件 |
| 不转换 TEX | 仅提取原始 TEX 文件，不转换为图片 |

## 项目结构

```
RePKG-GUI-Python/
├── repkg_gui.py          # 主程序入口
├── gui/
│   ├── __init__.py
│   ├── main_window.py    # 主窗口
│   ├── extract_tab.py    # 解包标签页 (支持拖放)
│   └── info_tab.py       # 信息查看标签页 (支持拖放)
├── core/
│   ├── __init__.py
│   └── repkg_runner.py   # RePKG CLI 封装
└── README.md
```

## 致谢

- **[RePKG](https://github.com/notscuffed/RePKG)** - 原始命令行工具，由 [NotScuffed](https://github.com/notscuffed) 开发
- **Steam Wallpaper Engine** - 壁纸引擎

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

RePKG 原项目同样使用 MIT License，详见 [RePKG LICENSE](https://github.com/notscuffed/RePKG/blob/master/LICENSE)。

## 相关链接

- RePKG 原项目: https://github.com/notscuffed/RePKG
- RePKG Releases: https://github.com/notscuffed/RePKG/releases
- Steam Wallpaper Engine: https://store.steampowered.com/app/431960/Wallpaper_Engine/

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

1. **项目性质**：本项目是 [RePKG](https://github.com/notscuffed/RePKG) 命令行工具的图形界面包装器（GUI Wrapper），仅提供更友好的操作界面，不包含 RePKG 的核心解包逻辑代码。

2. **版权归属**：RePKG 核心功能的所有权归原作者 [NotScuffed](https://github.com/notscuffed) 所有，本项目遵循原项目的 MIT License 进行分发。

3. **使用责任**：使用本工具解包的内容应仅限于个人学习、研究或备份已购买的 Wallpaper Engine 壁纸。用户应自行承担使用本工具所产生的一切法律责任。

4. **第三方内容**：通过本工具解包的壁纸内容版权归原作者所有，未经授权不得用于商业用途或重新分发。

5. **商标声明**：Steam 和 Wallpaper Engine 是 Valve Corporation 的注册商标。本项目与 Valve Corporation 无任何关联。

6. **免责声明**：本软件按"原样"提供，不作任何明示或暗示的保证。作者不对因使用本软件而导致的任何直接或间接损失承担责任。
