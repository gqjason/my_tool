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

class button:
    
    
    main_frame = ttk.Frame(self.root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 标题栏
    title_bar = ttk.Frame(main_frame)
    title_bar.pack(fill=tk.X, pady=(0, 10))
    
    # 标题
    title_label = ttk.Label(
        title_bar, 
        text="OJ比赛信息查询系统",
        font=(self.settings["font_family"], 24, "bold"),
        foreground="#2c3e50"
    )
    title_label.pack(side=tk.LEFT)
    
    # 设置按钮
    settings_button = ttk.Button(
        title_bar,
        text="⚙️",
        command=self.open_settings,
        width=2
    )
    settings_button.pack(side=tk.RIGHT, padx=5)
    
    # 副标题
    subtitle_label = ttk.Label(
        main_frame,
        text="获取最新的编程竞赛信息，及时准备比赛",
        font=(self.settings["font_family"], 12),
        foreground="#7f8c8d"
    )
    subtitle_label.pack(pady=(0, 15))
    
    # 按钮框架
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 15))
    
    # 按钮1 - 获取当天比赛数据
    self.today_button = ttk.Button(
        button_frame,
        text="获取当天的比赛数据",
        command=self.get_today_data,
        width=20,
        style="Primary.TButton"
    )
    self.today_button.pack(side=tk.LEFT, padx=10)
    
    # 按钮2 - 获取即将开始比赛数据
    self.upcoming_button = ttk.Button(
        button_frame,
        text="获取即将开始的比赛数据",
        command=self.get_upcoming_data,
        width=20,
        style="Secondary.TButton"
    )
    self.upcoming_button.pack(side=tk.LEFT, padx=10)
    
    # 复制按钮
    self.copy_button = ttk.Button(
        button_frame,
        text="复制选中文本",
        command=self.copy_selected_text,
        width=15
    )
    self.copy_button.pack(side=tk.RIGHT, padx=10)
    
    # 清空按钮
    self.clear_button = ttk.Button(
        button_frame,
        text="清空日志",
        command=self.clear_logs,
        width=15
    )
    self.clear_button.pack(side=tk.RIGHT, padx=10)
        
        
