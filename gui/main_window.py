# -*- coding: utf-8 -*-
"""
主窗口模块
提供 RePKG GUI 的主界面，包含解包和信息查看两个标签页，支持文件拖放
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

from .extract_tab import ExtractTab
from .info_tab import InfoTab
from core.repkg_runner import RePKGRunner


class MainWindow:
    """RePKG GUI 主窗口"""

    def __init__(self):
        """初始化主窗口"""
        # 如果支持拖放，使用 TkinterDnD.Tk() 替代 tk.Tk()
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        
        self.root.title("RePKG-GUI Python Edition v1.0")
        self.root.geometry("700x550")
        self.root.minsize(600, 450)
        
        # 尝试设置图标 (如果存在)
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # 初始化 RePKG 运行器
        try:
            self.runner = RePKGRunner()
        except FileNotFoundError as e:
            messagebox.showerror("错误", str(e))
            self.root.destroy()
            return
        
        # 创建界面
        self._create_menu()
        self._create_main_frame()
        self._create_status_bar()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开输出目录", command=self._open_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)

    def _create_main_frame(self):
        """创建主框架，包含标签页"""
        # 创建 Notebook (标签控件)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建解包标签页
        extract_frame = ttk.Frame(self.notebook)
        self.notebook.add(extract_frame, text="  解包 PKG  ")
        self.extract_tab = ExtractTab(extract_frame, self.runner)
        self.extract_tab.frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建信息查看标签页
        info_frame = ttk.Frame(self.notebook)
        self.notebook.add(info_frame, text="  查看信息  ")
        self.info_tab = InfoTab(info_frame, self.runner)
        self.info_tab.frame.pack(fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _open_output_dir(self):
        """打开输出目录"""
        import subprocess
        output_dir = "./output"
        if os.path.exists(output_dir):
            subprocess.Popen(f'explorer "{os.path.abspath(output_dir)}"')
        else:
            messagebox.showinfo("提示", "输出目录不存在")

    def _show_about(self):
        """显示关于对话框"""
        dnd_status = "支持" if HAS_DND else "未安装 tkinterdnd2"
        about_text = f"""RePKG-GUI Python Edition v1.0

基于 RePKG 命令行工具的图形界面包装器
用于解包 Steam Wallpaper Engine 壁纸文件

功能:
- 解包 PKG 文件
- 转换 TEX 文件为图片
- 查看 PKG/TEX 信息
- 支持文件拖放: {dnd_status}

RePKG 原作者: NotScuffed
GUI 封装: Python + tkinter"""
        messagebox.showinfo("关于", about_text)

    def _on_close(self):
        """关闭窗口"""
        if self.extract_tab.is_running or self.info_tab.is_running:
            if not messagebox.askyesno("确认", "有操作正在进行中，确定要退出吗？"):
                return
        self.root.destroy()

    def run(self):
        """运行主循环"""
        self.root.mainloop()
