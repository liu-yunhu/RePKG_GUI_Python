# -*- coding: utf-8 -*-
"""
信息查看标签页模块
提供查看 PKG/TEX 文件信息的图形界面，支持文件拖放
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


class InfoTab:
    """信息查看标签页"""

    def __init__(self, parent, runner):
        """
        初始化信息查看标签页
        
        Args:
            parent: 父容器
            runner: RePKGRunner 实例
        """
        self.parent = parent
        self.runner = runner
        self.is_running = False
        
        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.frame = ttk.Frame(self.parent, padding=10)
        
        # 输入文件
        input_frame = ttk.LabelFrame(self.frame, text="输入 (支持拖放)", padding=5)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="文件/目录:").pack(anchor=tk.W)
        
        input_path_frame = ttk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_path_frame, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 启用拖放功能
        if HAS_DND:
            self.input_entry.drop_target_register(DND_FILES)
            self.input_entry.dnd_bind('<<Drop>>', self._on_drop_input)
        
        ttk.Button(input_path_frame, text="浏览...", 
                   command=self._browse_input).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 拖拽提示
        if HAS_DND:
            hint_text = "(支持拖放 PKG/TEX 文件或目录)"
        else:
            hint_text = "(点击浏览选择 PKG/TEX 文件)"
        ttk.Label(input_frame, text=hint_text, 
                  foreground="gray").pack(anchor=tk.W, pady=(2, 0))
        
        # 选项
        options_frame = ttk.LabelFrame(self.frame, text="选项", padding=5)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行选项
        row1 = ttk.Frame(options_frame)
        row1.pack(fill=tk.X, pady=2)
        
        self.sort_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row1, text="排序条目", 
                        variable=self.sort_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.print_entries_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1, text="打印条目列表", 
                        variable=self.print_entries_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.tex_dir_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row1, text="TEX目录模式", 
                        variable=self.tex_dir_var).pack(side=tk.LEFT)
        
        # 排序方式
        row2 = ttk.Frame(options_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="排序方式:").pack(side=tk.LEFT)
        self.sort_by_var = tk.StringVar(value="name")
        sort_combo = ttk.Combobox(row2, textvariable=self.sort_by_var, 
                                  values=["name", "extension", "size"], 
                                  state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # 项目信息显示
        ttk.Label(row2, text="项目信息键:").pack(side=tk.LEFT)
        self.project_info_var = tk.StringVar(value="*")
        ttk.Entry(row2, textvariable=self.project_info_var, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # 标题过滤
        row3 = ttk.Frame(options_frame)
        row3.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(row3, text="标题过滤:").pack(side=tk.LEFT)
        self.title_filter_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.title_filter_var, width=30).pack(side=tk.LEFT, padx=(5, 0))
        
        # 操作按钮
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="查看信息", 
                                    command=self._start_info)
        self.start_btn.pack(side=tk.LEFT)
        
        # 日志输出
        log_frame = ttk.LabelFrame(self.frame, text="信息输出", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框和滚动条
        log_inner = ttk.Frame(log_frame)
        log_inner.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_inner, height=12, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_inner, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 清空日志按钮
        ttk.Button(log_frame, text="清空日志", 
                   command=self._clear_log).pack(anchor=tk.E, pady=(5, 0))

    def _on_drop_input(self, event):
        """处理输入框的拖放事件"""
        files = event.data
        
        if files.startswith('{') and files.endswith('}'):
            files = files[1:-1]
        
        if os.path.isdir(files):
            self.input_var.set(files)
        elif os.path.isfile(files):
            self.input_var.set(files)
        else:
            file_list = self._parse_drop_data(event.data)
            if file_list:
                first_file = file_list[0]
                if os.path.isdir(first_file) or os.path.isfile(first_file):
                    self.input_var.set(first_file)

    def _parse_drop_data(self, data: str) -> list:
        """解析拖放数据，处理带空格的路径"""
        files = []
        if data.startswith('{'):
            import re
            files = re.findall(r'\{([^}]+)\}', data)
            if not files:
                files = [data]
        else:
            files = data.split()
        return files

    def _browse_input(self):
        """浏览选择输入文件或目录"""
        # 先尝试选择文件
        file_path = filedialog.askopenfilename(
            title="选择 PKG 或 TEX 文件",
            filetypes=[
                ("PKG 文件", "*.pkg"),
                ("TEX 文件", "*.tex"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.input_var.set(file_path)
            return
        
        # 如果没选择文件，尝试选择目录
        dir_path = filedialog.askdirectory(title="选择包含 PKG/TEX 文件的目录")
        if dir_path:
            self.input_var.set(dir_path)

    def _log(self, message: str):
        """向日志框添加消息"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        """清空日志"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _start_info(self):
        """开始查看信息"""
        input_path = self.input_var.get().strip()
        if not input_path:
            messagebox.showwarning("提示", "请先选择输入文件或目录")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("错误", f"输入路径不存在: {input_path}")
            return
        
        self._clear_log()
        self._log(f"查看信息: {input_path}")
        self._log("-" * 50)
        
        # 禁用按钮
        self.is_running = True
        self.start_btn.configure(state=tk.DISABLED)
        
        # 异步执行
        self.runner.info_async(
            input_path=input_path,
            sort=self.sort_var.get(),
            sort_by=self.sort_by_var.get(),
            tex_dir=self.tex_dir_var.get(),
            project_info=self.project_info_var.get().strip() or None,
            print_entries=self.print_entries_var.get(),
            title_filter=self.title_filter_var.get().strip() or None,
            callback=lambda msg: self.parent.after(0, self._log, msg),
            done_callback=lambda code: self.parent.after(0, self._on_info_done, code)
        )

    def _on_info_done(self, return_code: int):
        """信息查看完成回调"""
        self.is_running = False
        self.start_btn.configure(state=tk.NORMAL)
        
        self._log("-" * 50)
        if return_code == 0:
            self._log("查询完成!")
        else:
            self._log(f"查询过程中出现错误 (返回码: {return_code})")
