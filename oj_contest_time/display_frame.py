import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Frame, Label, Entry, Button, Checkbutton, IntVar, StringVar
import threading
import queue
import time
import pyperclip
import json
import os
import sys
import platform
from get_information.capture import Main

class theApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OJ比赛信息查询系统")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        
        # 初始化UI
        self.create_main_widgets()
        
        
    def create_main_widgets(self):
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        title_bar = ttk.Frame(main_frame)
        title_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 文本区域
        text_frame = ttk.LabelFrame(main_frame, text="比赛信息")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        #正标题
        title_label = ttk.Label(
            title_bar, 
            text="OJ比赛信息查询系统",
            font=("Microsoft YaHei", 24, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack()
        
        # 副标题
        subtitle_label = ttk.Label(
            title_bar,
            text="获取最新的编程竞赛信息，及时准备比赛",
            font=("Microsoft YaHei", 12),
            foreground="#7f8c8d"
        )
        subtitle_label.pack()
        
        
        # 设置按钮
        setting_button = tk.Button(
            title_bar,  
            text="⚙️设置",       
            command=self.button_click, 
            width=15
            
        )
        setting_button.pack(side=tk.RIGHT, padx=10)

        #获取今天比赛信息
        getting_today_upcoming_information_button = tk.Button(
            button_frame,
            text= "获取今天比赛信息",
            command=self.button_click,
            width=20
            #style="Primary.TButton"
        )
        getting_today_upcoming_information_button.pack(side=tk.LEFT, padx=(5,5))

        #获取接下来比赛信息
        getting_all_upcoming_information_button = tk.Button(
            button_frame,
            text= "获取接下来比赛信息",
            command=self.button_click,
            width=20
            #style="Primary.TButton"
        )
        getting_all_upcoming_information_button.pack(side=tk.LEFT, padx=(15,0))

        # 清空按钮
        clear_button = tk.Button(
            button_frame,
            text="清空窗口",
            command=self.button_click,
            width=15
            
        )
        clear_button.pack(side=tk.RIGHT, padx=10)
        

        # 创建带滚动条的文本框
        text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        
    def button_click(self):  # 添加self参数
        print("Button clicked!")





if __name__ == "__main__":
    root = tk.Tk()
    app = theApp(root)
    root.mainloop()