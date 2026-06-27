# -*- coding: utf-8 -*-
"""
解包功能标签页模块
提供 PKG 文件解包和 TEX 文件转换的图形界面，支持文件拖放
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


class ExtractTab:
    """解包功能标签页"""

    def __init__(self, parent, runner):
        """
        初始化解包标签页
        
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
        
        # 输入文件/目录
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
            hint_text = "(点击浏览选择 PKG 文件或包含 TEX 文件的目录)"
        ttk.Label(input_frame, text=hint_text, 
                  foreground="gray").pack(anchor=tk.W, pady=(2, 0))
        
        # 输出目录
        output_frame = ttk.LabelFrame(self.frame, text="输出 (支持拖放)", padding=5)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="输出目录:").pack(anchor=tk.W)
        
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.output_var = tk.StringVar(value="./output")
        self.output_entry = ttk.Entry(output_path_frame, textvariable=self.output_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 启用拖放功能
        if HAS_DND:
            self.output_entry.drop_target_register(DND_FILES)
            self.output_entry.dnd_bind('<<Drop>>', self._on_drop_output)
        
        ttk.Button(output_path_frame, text="浏览...", 
                   command=self._browse_output).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 选项
        options_frame = ttk.LabelFrame(self.frame, text="选项", padding=5)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行选项
        row1 = ttk.Frame(options_frame)
        row1.pack(fill=tk.X, pady=2)
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1, text="递归搜索子目录", 
                        variable=self.recursive_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.copy_project_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1, text="复制项目文件", 
                        variable=self.copy_project_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.use_name_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1, text="使用项目名称", 
                        variable=self.use_name_var).pack(side=tk.LEFT)
        
        # 第二行选项
        row2 = ttk.Frame(options_frame)
        row2.pack(fill=tk.X, pady=2)
        
        self.single_dir_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="单目录输出", 
                        variable=self.single_dir_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="覆盖已有文件", 
                        variable=self.overwrite_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.no_tex_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="不转换TEX", 
                        variable=self.no_tex_var).pack(side=tk.LEFT)
        
        # 扩展名过滤
        filter_frame = ttk.Frame(options_frame)
        filter_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(filter_frame, text="仅提取扩展名:").pack(side=tk.LEFT)
        self.only_exts_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.only_exts_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(filter_frame, text="忽略扩展名:").pack(side=tk.LEFT)
        self.ignore_exts_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.ignore_exts_var, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # 操作按钮
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="开始解包", 
                                    command=self._start_extract)
        self.start_btn.pack(side=tk.LEFT)
        
        self.stop_btn = ttk.Button(button_frame, text="停止", 
                                   command=self._stop_extract, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.open_dir_btn = ttk.Button(button_frame, text="打开输出目录", 
                                       command=self._open_output_dir, state=tk.DISABLED)
        self.open_dir_btn.pack(side=tk.RIGHT)
        
        # 日志输出
        log_frame = ttk.LabelFrame(self.frame, text="日志输出", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框和滚动条
        log_inner = ttk.Frame(log_frame)
        log_inner.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_inner, height=10, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_inner, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 清空日志按钮
        ttk.Button(log_frame, text="清空日志", 
                   command=self._clear_log).pack(anchor=tk.E, pady=(5, 0))

    def _on_drop_input(self, event):
        """处理输入框的拖放事件"""
        # 获取拖放的文件路径
        files = event.data
        
        # 处理路径中的大括号 (Windows 路径可能包含空格，tkinterdnd2 会用大括号包裹)
        if files.startswith('{') and files.endswith('}'):
            files = files[1:-1]
        
        # 检查是否是目录
        if os.path.isdir(files):
            self.input_var.set(files)
            self.output_var.set(os.path.join(files, 'output'))
        elif os.path.isfile(files):
            self.input_var.set(files)
            parent_dir = os.path.dirname(files)
            self.output_var.set(os.path.join(parent_dir, 'output'))
        else:
            # 尝试解析多个文件 (取第一个)
            file_list = self._parse_drop_data(event.data)
            if file_list:
                first_file = file_list[0]
                if os.path.isdir(first_file):
                    self.input_var.set(first_file)
                    self.output_var.set(os.path.join(first_file, 'output'))
                elif os.path.isfile(first_file):
                    self.input_var.set(first_file)
                    parent_dir = os.path.dirname(first_file)
                    self.output_var.set(os.path.join(parent_dir, 'output'))

    def _on_drop_output(self, event):
        """处理输出框的拖放事件"""
        files = event.data
        
        if files.startswith('{') and files.endswith('}'):
            files = files[1:-1]
        
        if os.path.isdir(files):
            self.output_var.set(files)
        elif os.path.isfile(files):
            self.output_var.set(os.path.dirname(files))
        else:
            file_list = self._parse_drop_data(event.data)
            if file_list:
                first_file = file_list[0]
                if os.path.isdir(first_file):
                    self.output_var.set(first_file)
                elif os.path.isfile(first_file):
                    self.output_var.set(os.path.dirname(first_file))

    def _parse_drop_data(self, data: str) -> list:
        """解析拖放数据，处理带空格的路径"""
        files = []
        if data.startswith('{'):
            # 处理用大括号包裹的路径
            import re
            files = re.findall(r'\{([^}]+)\}', data)
            # 如果没有大括号包裹的路径，可能是单个无空格路径
            if not files:
                files = [data]
        else:
            # 空格分隔的多个文件
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
            parent_dir = os.path.dirname(file_path)
            self.output_var.set(os.path.join(parent_dir, 'output'))
            return
        
        # 如果没选择文件，尝试选择目录
        dir_path = filedialog.askdirectory(title="选择包含 PKG/TEX 文件的目录")
        if dir_path:
            self.input_var.set(dir_path)
            self.output_var.set(os.path.join(dir_path, 'output'))

    def _browse_output(self):
        """浏览选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_var.set(dir_path)

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

    def _start_extract(self):
        """开始解包"""
        input_path = self.input_var.get().strip()
        if not input_path:
            messagebox.showwarning("提示", "请先选择输入文件或目录")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("错误", f"输入路径不存在: {input_path}")
            return
        
        output_dir = self.output_var.get().strip() or './output'
        
        self._clear_log()
        self._log(f"开始解包...")
        self._log(f"输入: {input_path}")
        self._log(f"输出: {output_dir}")
        self._log("-" * 50)
        
        # 禁用按钮
        self.is_running = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.open_dir_btn.configure(state=tk.DISABLED)
        
        # 异步执行
        self.runner.extract_async(
            input_path=input_path,
            output_dir=output_dir,
            recursive=self.recursive_var.get(),
            copy_project=self.copy_project_var.get(),
            use_name=self.use_name_var.get(),
            single_dir=self.single_dir_var.get(),
            overwrite=self.overwrite_var.get(),
            no_tex_convert=self.no_tex_var.get(),
            ignore_exts=self.ignore_exts_var.get().strip() or None,
            only_exts=self.only_exts_var.get().strip() or None,
            callback=lambda msg: self.parent.after(0, self._log, msg),
            done_callback=lambda code: self.parent.after(0, self._on_extract_done, code)
        )

    def _on_extract_done(self, return_code: int):
        """解包完成回调"""
        self.is_running = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        
        self._log("-" * 50)
        if return_code == 0:
            self._log("解包完成!")
            self.open_dir_btn.configure(state=tk.NORMAL)
            # 弹窗询问是否打开输出目录
            if messagebox.askyesno("完成", "解包操作已完成，是否打开输出目录？"):
                self._open_output_dir()
        else:
            self._log(f"解包过程中出现错误 (返回码: {return_code})")

    def _open_output_dir(self):
        """打开输出目录"""
        import subprocess
        output_dir = self.output_var.get().strip()
        if not output_dir:
            output_dir = './output'
        
        output_dir = os.path.abspath(output_dir)
        if os.path.exists(output_dir):
            subprocess.Popen(f'explorer "{output_dir}"')
        else:
            messagebox.showinfo("提示", f"输出目录不存在: {output_dir}")

    def _stop_extract(self):
        """停止解包 (目前仅禁用按钮，无法真正终止子进程)"""
        self._log("正在停止...")
        # 注意: subprocess 无法直接终止，这里只是 UI 状态更新
        self.is_running = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
