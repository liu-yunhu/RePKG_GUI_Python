# -*- coding: utf-8 -*-
"""
RePKG 命令行工具封装模块
封装 RePKG.exe 的 extract 和 info 命令，提供 Python 调用接口
"""

import subprocess
import os
import sys
import threading
from typing import Callable, Optional, Dict


class RePKGRunner:
    """RePKG.exe 命令行工具调用封装类"""

    def __init__(self, repkg_path: str = None):
        """
        初始化 RePKG 运行器
        
        Args:
            repkg_path: RePKG.exe 的路径，默认为程序目录下的 RePKG.exe
        """
        if repkg_path is None:
            # 获取程序所在目录 (兼容 PyInstaller 打包和直接运行)
            if getattr(sys, 'frozen', False):
                # PyInstaller 打包后，exe 所在目录
                app_dir = os.path.dirname(sys.executable)
            else:
                # 直接运行 Python 脚本，脚本所在目录
                app_dir = os.path.dirname(os.path.abspath(__file__))
                app_dir = os.path.dirname(app_dir)  # 上一级目录
            repkg_path = os.path.join(app_dir, 'RePKG.exe')
        
        self.repkg_path = os.path.abspath(repkg_path)
        
        if not os.path.exists(self.repkg_path):
            raise FileNotFoundError(f"找不到 RePKG.exe: {self.repkg_path}")

    def extract(self, 
                input_path: str, 
                output_dir: str = './output',
                recursive: bool = False,
                copy_project: bool = False,
                use_name: bool = False,
                tex_dir: bool = False,
                single_dir: bool = False,
                no_tex_convert: bool = False,
                overwrite: bool = False,
                ignore_exts: str = None,
                only_exts: str = None,
                callback: Optional[Callable[[str], None]] = None) -> int:
        """
        执行 extract 命令，解包 PKG 文件或转换 TEX 文件
        
        Args:
            input_path: 输入文件或目录路径
            output_dir: 输出目录
            recursive: 递归搜索子目录
            copy_project: 复制 project.json 和预览图
            use_name: 使用 project.json 中的名称作为子目录名
            tex_dir: 将目录中的 TEX 文件转换为图片
            single_dir: 所有文件输出到同一目录
            no_tex_convert: 不将 TEX 转换为图片
            overwrite: 覆盖已有文件
            ignore_exts: 忽略指定扩展名 (逗号分隔)
            only_exts: 仅提取指定扩展名 (逗号分隔)
            callback: 输出回调函数，每行输出调用一次
            
        Returns:
            进程返回码
        """
        cmd = [self.repkg_path, 'extract']
        
        # 添加选项参数
        if recursive:
            cmd.append('-r')
        if copy_project:
            cmd.append('-c')
        if use_name:
            cmd.append('-n')
        if tex_dir:
            cmd.append('-t')
        if single_dir:
            cmd.append('-s')
        if no_tex_convert:
            cmd.append('--no-tex-convert')
        if overwrite:
            cmd.append('--overwrite')
        
        # 添加输出目录
        cmd.extend(['-o', output_dir])
        
        # 添加扩展名过滤
        if ignore_exts:
            cmd.extend(['-i', ignore_exts])
        if only_exts:
            cmd.extend(['-e', only_exts])
        
        # 添加输入路径 (必须在最后)
        cmd.append(input_path)
        
        return self._run_command(cmd, callback)

    def info(self,
             input_path: str,
             sort: bool = False,
             sort_by: str = 'name',
             tex_dir: bool = False,
             project_info: str = None,
             print_entries: bool = False,
             title_filter: str = None,
             callback: Optional[Callable[[str], None]] = None) -> int:
        """
        执行 info 命令，显示 PKG/TEX 信息
        
        Args:
            input_path: 输入文件或目录路径
            sort: 排序条目
            sort_by: 排序方式 (name, extension, size)
            tex_dir: 显示目录中所有 TEX 文件信息
            project_info: 要显示的 project.json 键 (逗号分隔，* 显示全部)
            print_entries: 打印包中的条目
            title_filter: 标题过滤器
            callback: 输出回调函数
            
        Returns:
            进程返回码
        """
        cmd = [self.repkg_path, 'info']
        
        # 添加选项参数
        if sort:
            cmd.append('-s')
        if sort_by != 'name':
            cmd.extend(['-b', sort_by])
        if tex_dir:
            cmd.append('-t')
        if project_info:
            cmd.extend(['-p', project_info])
        if print_entries:
            cmd.append('-e')
        if title_filter:
            cmd.extend(['--title-filter', title_filter])
        
        # 添加输入路径
        cmd.append(input_path)
        
        return self._run_command(cmd, callback)

    def _run_command(self, cmd: list, callback: Optional[Callable[[str], None]] = None) -> int:
        """
        执行命令并实时输出结果
        
        Args:
            cmd: 命令参数列表
            callback: 输出回调函数
            
        Returns:
            进程返回码
        """
        try:
            # 创建进程，捕获输出
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # 实时读取输出
            for line in process.stdout:
                line = line.rstrip('\n\r')
                if callback:
                    callback(line)
            
            process.wait()
            return process.returncode
            
        except FileNotFoundError:
            if callback:
                callback(f"错误: 找不到 RePKG.exe - {self.repkg_path}")
            return -1
        except Exception as e:
            if callback:
                callback(f"错误: {str(e)}")
            return -1

    def extract_async(self,
                      input_path: str,
                      output_dir: str = './output',
                      callback: Optional[Callable[[str], None]] = None,
                      done_callback: Optional[Callable[[int], None]] = None,
                      **kwargs) -> threading.Thread:
        """
        异步执行 extract 命令
        
        Args:
            input_path: 输入文件或目录路径
            output_dir: 输出目录
            callback: 输出回调函数
            done_callback: 完成回调函数，参数为返回码
            **kwargs: 其他 extract 参数
            
        Returns:
            线程对象
        """
        def run():
            return_code = self.extract(input_path, output_dir, callback=callback, **kwargs)
            if done_callback:
                done_callback(return_code)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def info_async(self,
                   input_path: str,
                   callback: Optional[Callable[[str], None]] = None,
                   done_callback: Optional[Callable[[int], None]] = None,
                   **kwargs) -> threading.Thread:
        """
        异步执行 info 命令
        
        Args:
            input_path: 输入文件或目录路径
            callback: 输出回调函数
            done_callback: 完成回调函数
            **kwargs: 其他 info 参数
            
        Returns:
            线程对象
        """
        def run():
            return_code = self.info(input_path, callback=callback, **kwargs)
            if done_callback:
                done_callback(return_code)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread


# 便捷函数
def get_runner(repkg_path: str = None) -> RePKGRunner:
    """获取 RePKGRunner 实例"""
    return RePKGRunner(repkg_path)
