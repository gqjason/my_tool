# app/ui.py
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
from .setting.setting_ui import SettingsDialog
from .setting.setting_logic import SettingsManager
class AppUI:
    """负责应用程序的用户界面"""
    def __init__(self, root, logic):
        self.root = root
        self.logic = logic  # 引用逻辑类的实例
        
        # 设置UI回调
        self.logic.ui_callback = self.update_ui
        
        self.root.title("OJ比赛信息查询系统")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        
        self.create_main_widgets()
    
    def create_main_widgets(self):
        """创建主界面组件"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        title_bar = ttk.Frame(main_frame)
        title_bar.pack(fill=tk.X, pady=(0, 10))
        self.create_title_bar(title_bar)
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        self.create_buttons(button_frame)
        # 状态栏
        status_bar = ttk.Frame(main_frame)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.create_status_bar(status_bar)        
        
        # 文本区域框架
        text_frame = ttk.LabelFrame(main_frame, text="比赛信息")
        text_frame.pack(fill=tk.BOTH, expand=True)
        self.create_text_area(text_frame)

        # 创建UI元素
        
        
        
        
    
    def create_title_bar(self, parent):
        """创建标题栏"""
        # 主标题
        title_label = ttk.Label(
            parent, 
            text="OJ比赛信息查询系统",
            font=("Microsoft YaHei", 24, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack()
        
        # 副标题
        subtitle_label = ttk.Label(
            parent,
            text="获取最新的编程竞赛信息，及时准备比赛",
            font=("Microsoft YaHei", 12),
            foreground="#7f8c8d"
        )
        subtitle_label.pack()
        
        # 设置按钮
        self.setting_button = tk.Button(
            parent,  
            text="⚙️设置",       
            command=self.open_settings,
            width=15
        )
        self.setting_button.pack(side=tk.RIGHT, padx=10)
    
    def create_buttons(self, parent):
        """创建功能按钮"""
        # 获取今天比赛信息按钮
        self.today_button = tk.Button(
            parent,
            text="获取今天比赛信息",
            command=self.logic.get_today_data,
            width=20
        )
        self.today_button.pack(side=tk.LEFT, padx=5)
        
        # 获取接下来比赛信息按钮
        self.upcoming_button = tk.Button(
            parent,
            text="获取接下来比赛信息",
            command=self.logic.get_upcoming_data,
            width=20
        )
        self.upcoming_button.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        self.clear_button = tk.Button(
            parent,
            text="清空窗口",
            command=self.logic.clear_logs,
            width=15
        )
        self.clear_button.pack(side=tk.RIGHT, padx=10)
    
    def create_text_area(self, parent):
        """创建文本区域"""
        # 创建带滚动条的文本框
        self.text_area = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            font=("Microsoft YaHei", 11)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5,5))
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, "欢迎使用OJ比赛信息查询系统！\n")
        self.text_area.config(state=tk.DISABLED)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        self.status_label = ttk.Label(
            parent,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady = (5,5))
    
    def update_ui(self, message, clear=False):
        """更新UI界面（从逻辑类回调）"""
        # 使用after方法在主线程中安全更新UI
        self.root.after(0, lambda: self._update_ui_safe(message, clear))
    
    def _update_ui_safe(self, message, clear):
        """安全更新UI（在主线程中执行）"""
        if message == "clear":
            # 清空日志
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "日志已清空\n")
            self.text_area.config(state=tk.DISABLED)
            return
        
        if clear:
            # 清空并添加新内容
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, message)
            self.text_area.see(tk.END)
            self.text_area.config(state=tk.DISABLED)
        elif "状态:" not in message:
            # 添加新内容
            self.text_area.config(state=tk.NORMAL)
            self.text_area.insert(tk.END, message)
            self.text_area.see(tk.END)
            self.text_area.config(state=tk.DISABLED)
    
        if "状态:" in message:
            self.status_label.config(text=message)
    
    def open_settings(self):
        """打开设置对话框"""
        # 从逻辑类获取当前配置
        # 创建设置对话框
        self.settings_manager = SettingsManager()
        SettingsDialog(
            self.root,self.settings_manager
        )