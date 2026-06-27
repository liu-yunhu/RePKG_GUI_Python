# -*- coding: utf-8 -*-
"""
RePKG-GUI Python Edition
主程序入口
"""

import sys
import os

# 将当前目录添加到模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from gui.main_window import MainWindow


def main():
    """主函数"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")
        sys.exit(1)


if __name__ == '__main__':
    main()
