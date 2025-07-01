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

# 获取配置文件路径
def get_config_path():
    if platform.system() == "Windows":
        return os.path.join(os.getenv('APPDATA'), "OJContestApp", "settings.json")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "OJContestApp", "settings.json")

# 创建配置目录
def create_config_dir():
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_path

# 开机自启动设置
def set_autostart(enable):
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)
    
    if platform.system() == "Windows":
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "OJContestApp"
        app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except WindowsError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"设置开机自启动失败: {e}")
            return False
    
    elif platform.system() == "Darwin":  # macOS
        launchd_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(launchd_dir, "com.ojcontestapp.plist")
        
        if enable:
            if not os.path.exists(launchd_dir):
                os.makedirs(launchd_dir)
            
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ojcontestapp</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.abspath(sys.argv[0])}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
            
            with open(plist_path, "w") as f:
                f.write(plist_content)
            return True
        else:
            if os.path.exists(plist_path):
                os.remove(plist_path)
            return True
    
    elif platform.system() == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_path = os.path.join(autostart_dir, "ojcontestapp.desktop")
        
        if enable:
            if not os.path.exists(autostart_dir):
                os.makedirs(autostart_dir)
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=OJ Contest App
Exec={sys.executable} {os.path.abspath(sys.argv[0])}
Comment=OJ比赛信息查询系统
X-GNOME-Autostart-enabled=true
"""
            
            with open(desktop_path, "w") as f:
                f.write(desktop_content)
            return True
        else:
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
            return True
    
    return False

# 检查开机自启动状态
def check_autostart():
    if platform.system() == "Windows":
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "OJContestApp"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, app_name)
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except:
            return False
    
    elif platform.system() == "Darwin":  # macOS
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.ojcontestapp.plist")
        return os.path.exists(plist_path)
    
    elif platform.system() == "Linux":
        desktop_path = os.path.expanduser("~/.config/autostart/ojcontestapp.desktop")
        return os.path.exists(desktop_path)
    
    return False

class OJContestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OJ比赛信息查询系统")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        
        # 创建队列用于线程通信
        self.message_queue = queue.Queue()
        
        # 运行状态
        self.running = False
        
        # 加载配置
        self.settings = self.load_settings()
        
        # 初始化UI
        self.create_widgets()
        
        # 启动消息检查
        self.check_queue()
        
        # 设置主题
        self.apply_theme(self.settings["theme"])
    
    def load_settings(self):
        """加载配置文件"""
        default_settings = {
            "auto_refresh": False,
            "refresh_interval": 30,
            "notify_before": 60,
            "show_platforms": ["Codeforces", "AtCoder", "牛客"],
            "theme": "light",
            "autostart": check_autostart(),
            "font_size": 10,
            "font_family": "Microsoft YaHei"
        }
        
        config_path = create_config_dir()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # 确保所有设置项都存在
                    for key in default_settings:
                        if key not in settings:
                            settings[key] = default_settings[key]
                    return settings
            except:
                return default_settings
        return default_settings
    
    def save_settings(self):
        """保存设置到文件"""
        config_path = create_config_dir()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False
    
    def apply_theme(self, theme):
        """应用主题设置"""
        if theme == "dark":
            self.root.configure(bg="#2d2d2d")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(".", background="#2d2d2d", foreground="#e0e0e0")
            style.configure("TFrame", background="#2d2d2d")
            style.configure("TLabel", background="#2d2d2d", foreground="#e0e0e0")
            style.configure("TLabelframe", background="#3d3d3d", foreground="#e0e0e0")
            style.configure("TLabelframe.Label", background="#3d3d3d", foreground="#e0e0e0")
            style.configure("TButton", background="#444", foreground="#e0e0e0")
            style.configure("Primary.TButton", background="#0D00FF", foreground="#ffffff")
            style.configure("Secondary.TButton", background="#FF0000", foreground="#ffffff")
            style.map("TButton", background=[("active", "#555")])
            style.map("Primary.TButton", background=[("active", "#6054FF")])
            style.map("Secondary.TButton", background=[("active", "#FF4C4C")])
            
            # 文本区域
            self.text_area.configure(bg="#3d3d3d", fg="#e0e0e0", insertbackground="#e0e0e0")
        else:
            self.root.configure(bg="#f0f0f0")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(".", background="#f0f0f0", foreground="#000000")
            style.configure("TFrame", background="#f0f0f0")
            style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("TLabelframe", background="#ffffff", foreground="#000000")
            style.configure("TLabelframe.Label", background="#ffffff", foreground="#000000")
            style.configure("TButton", background="#e0e0e0", foreground="#000000")
            style.configure("Primary.TButton", background="#CDCAFF", foreground="#ffffff")
            style.configure("Secondary.TButton", background="#FFBFBF", foreground="#ffffff")
            style.map("TButton", background=[("active", "#d0d0d0")])
            style.map("Primary.TButton", background=[("active", "#6054FF")])
            style.map("Secondary.TButton", background=[("active", "#FF4C4C")])
            
            # 文本区域
            self.text_area.configure(bg="#ffffff", fg="#000000", insertbackground="#000000")
    
    def create_widgets(self):
        # 创建主框架
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
        
        # 文本区域
        text_frame = ttk.LabelFrame(main_frame, text="比赛信息")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建带滚动条的文本框
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=(self.settings["font_family"], self.settings["font_size"]),
            padx=10,
            pady=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加初始文本
        self.add_text("OJ比赛信息查询系统\n")
        self.add_text("系统初始化完成...\n")
        self.add_text("等待用户操作...\n")
        self.add_text("点击上方按钮开始执行\n")
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("状态: 已停止")
        
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = ttk.Label(
            status_bar, 
            textvariable=self.status_var,
            font=(self.settings["font_family"], 9),
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, padx=5)
        
        # 版权信息
        copyright_label = ttk.Label(
            status_bar,
            text="OJ比赛信息查询系统 v1.0 © 2023",
            font=(self.settings["font_family"], 9),
            foreground="#7f8c8d",
            anchor=tk.E
        )
        copyright_label.pack(side=tk.RIGHT, padx=5)
        
        # 配置样式
        self.configure_styles()
    
    def configure_styles(self):
        style = ttk.Style()
        
        # 主按钮样式
        style.configure("Primary.TButton", 
                        foreground="#ffffff", 
                        background="#0D00FF", 
                        font=(self.settings["font_family"], 10, "bold"))
        style.map("Primary.TButton",
                  background=[("active", "#6054FF"), ("pressed", "#0000AA")])
        
        # 次要按钮样式
        style.configure("Secondary.TButton", 
                        foreground="#ffffff", 
                        background="#FF0000", 
                        font=(self.settings["font_family"], 10, "bold"))
        style.map("Secondary.TButton",
                  background=[("active", "#FF4C4C"), ("pressed", "#AA0000")])
        
        # 文本区域标签样式
        style.configure("TLabelframe", font=(self.settings["font_family"], 10, "bold"))
        style.configure("TLabelframe.Label", foreground="#151515")
    
    def add_text(self, text):
        """添加文本到文本区域"""
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)  # 滚动到底部
    
    def get_today_data(self):
        """获取当天比赛数据"""
        if not self.running:
            self.running = True
            self.status_var.set("状态: 运行中...")
            self.today_button.state(["disabled"])
            self.upcoming_button.state(["disabled"])
            
            # 清空文本区域
            self.text_area.delete(1.0, tk.END)
            self.add_text("开始获取今天的比赛数据...\n")
            
            # 在新线程中运行
            threading.Thread(target=self.run_in_today_thread, daemon=True).start()
    
    def get_upcoming_data(self):
        """获取即将开始比赛数据"""
        if not self.running:
            self.running = True
            self.status_var.set("状态: 运行中...")
            self.today_button.state(["disabled"])
            self.upcoming_button.state(["disabled"])
            
            # 清空文本区域
            self.text_area.delete(1.0, tk.END)
            self.add_text("开始获取即将开始的比赛数据...\n")
            
            # 在新线程中运行
            threading.Thread(target=self.run_in_upcoming_thread, daemon=True).start()
    
    def clear_logs(self):
        """清空日志"""
        self.text_area.delete(1.0, tk.END)
        self.add_text("日志已清空\n")
        self.add_text("等待操作...\n")
    
    def copy_selected_text(self):
        """复制选中文本到剪贴板"""
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            pyperclip.copy(selected_text)
            self.add_text("已复制选中文本到剪贴板\n")
        except:
            messagebox.showinfo("提示", "请先选择要复制的文本")
    
    def run_in_today_thread(self):
        """在后台线程中获取当天比赛数据"""
        try:
            self.add_text("> 正在获取比赛数据...\n")
            time.sleep(1)  # 模拟网络请求
            
            today_contest = Main.return_today_upcoming_contest()
            self.text_area.delete(1.0, tk.END)
            self.add_text("[OJ_Bot]\n")
            if not today_contest:
                self.add_text("今天没有即将开始的比赛\n")
            else:
                for contest in today_contest:
                    self.add_text("-" * 60 + "\n")
                    self.add_text(f"比赛平台：{contest['platform']}\n")
                    self.add_text(f"比赛链接: {contest['link']}\n")
                    self.add_text(f"比赛标题: {contest['title']}\n")
                    self.add_text(f"比赛时间: {contest['time']}\n")
                    self.add_text(f"比赛时长: {contest['duration']}\n")
            
            self.add_text("> 数据获取完成！\n")
        except Exception as e:
            self.add_text(f"> 错误: {str(e)}\n")
        finally:
            self.running = False
            self.status_var.set("状态: 已停止")
            self.today_button.state(["!disabled"])
            self.upcoming_button.state(["!disabled"])
    
    def run_in_upcoming_thread(self):
        """在后台线程中获取即将开始比赛数据"""
        try:
            self.add_text("> 正在获取比赛数据...\n")
            time.sleep(1)  # 模拟网络请求
            
            upcoming_contest = Main.return_all_upcoming_contest()
            self.text_area.delete(1.0, tk.END)
            self.add_text("[OJ_Bot]\n")
            if not upcoming_contest:
                self.add_text("接下来没有即将开始的比赛\n")
            else:
                for contest in upcoming_contest:
                    self.add_text("-" * 60 + "\n")
                    self.add_text(f"比赛平台：{contest['platform']}\n")
                    self.add_text(f"比赛链接: {contest['link']}\n")
                    self.add_text(f"比赛标题: {contest['title']}\n")
                    self.add_text(f"比赛时间: {contest['time']}\n")
                    self.add_text(f"比赛时长: {contest['duration']}\n")
            
            self.add_text("> 数据获取完成！\n")
        except Exception as e:
            self.add_text(f"> 错误: {str(e)}\n")
        finally:
            self.running = False
            self.status_var.set("状态: 已停止")
            self.today_button.state(["!disabled"])
            self.upcoming_button.state(["!disabled"])
    
    def open_settings(self):
        """打开设置窗口"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("系统设置")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)  # 设置为主窗口的临时窗口
        settings_window.grab_set()  # 模态窗口
        
        # 设置窗口框架
        settings_frame = ttk.Frame(settings_window, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置标题
        ttk.Label(
            settings_frame,
            text="系统设置",
            font=(self.settings["font_family"], 16, "bold"),
            foreground="#2c3e50"
        ).pack(pady=(0, 20))
        
        # 创建选项卡
        notebook = ttk.Notebook(settings_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 常规设置选项卡
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text="常规设置")
        
        # 通知设置选项卡
        notify_frame = ttk.Frame(notebook, padding=10)
        notebook.add(notify_frame, text="通知设置")
        
        # 界面设置选项卡
        ui_frame = ttk.Frame(notebook, padding=10)
        notebook.add(ui_frame, text="界面设置")
        
        # 填充常规设置选项卡
        self.create_general_settings(general_frame)
        
        # 填充通知设置选项卡
        self.create_notify_settings(notify_frame)
        
        # 填充界面设置选项卡
        self.create_ui_settings(ui_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="保存设置",
            command=lambda: self.save_settings(settings_window),
            style="Primary.TButton",
            width=10
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=settings_window.destroy,
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def create_general_settings(self, frame):
        """创建常规设置选项卡内容"""
        # 自动刷新设置
        self.auto_refresh_var = tk.IntVar(value=int(self.settings["auto_refresh"]))
        auto_refresh_check = ttk.Checkbutton(
            frame,
            text="自动刷新比赛数据",
            variable=self.auto_refresh_var,
            onvalue=1,
            offvalue=0
        )
        auto_refresh_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 刷新间隔
        refresh_frame = ttk.Frame(frame)
        refresh_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(refresh_frame, text="刷新间隔(分钟):").pack(side=tk.LEFT, padx=(0, 5))
        self.refresh_interval_var = tk.StringVar(value=str(self.settings["refresh_interval"]))
        refresh_entry = ttk.Entry(refresh_frame, textvariable=self.refresh_interval_var, width=5)
        refresh_entry.pack(side=tk.LEFT)
        
        # 开机自启动
        self.autostart_var = tk.IntVar(value=int(self.settings["autostart"]))
        autostart_check = ttk.Checkbutton(
            frame,
            text="开机自动启动",
            variable=self.autostart_var,
            onvalue=1,
            offvalue=0
        )
        autostart_check.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # 平台选择
        ttk.Label(frame, text="显示比赛平台:", font=(self.settings["font_family"], 9, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        platforms = ["Codeforces", "AtCoder", "牛客"]
        self.platform_vars = {}
        
        for i, platform in enumerate(platforms):
            var = tk.IntVar(value=1 if platform in self.settings["show_platforms"] else 0)
            self.platform_vars[platform] = var
            
            cb = ttk.Checkbutton(
                frame,
                text=platform,
                variable=var,
                onvalue=1,
                offvalue=0
            )
            cb.grid(row=4 + i, column=0, sticky=tk.W, padx=20)
    
    def create_notify_settings(self, frame):
        """创建通知设置选项卡内容"""
        # 比赛开始前通知
        notify_frame = ttk.Frame(frame)
        notify_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(notify_frame, text="比赛开始前通知(分钟):").pack(side=tk.LEFT, padx=(0, 5))
        self.notify_before_var = tk.StringVar(value=str(self.settings["notify_before"]))
        notify_entry = ttk.Entry(notify_frame, textvariable=self.notify_before_var, width=5)
        notify_entry.pack(side=tk.LEFT)
        
        # 通知方式
        ttk.Label(frame, text="通知方式:", font=(self.settings["font_family"], 9, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.desktop_notify_var = tk.IntVar(value=1)
        desktop_check = ttk.Checkbutton(
            frame,
            text="桌面通知",
            variable=self.desktop_notify_var,
            onvalue=1,
            offvalue=0
        )
        desktop_check.pack(anchor=tk.W, padx=20)
    
    def create_ui_settings(self, frame):
        """创建界面设置选项卡内容"""
        # 主题选择
        ttk.Label(frame, text="界面主题:", font=(self.settings["font_family"], 9, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        themes = ["浅色模式", "深色模式", "自动跟随系统"]
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        
        for theme in themes:
            rb = ttk.Radiobutton(
                frame,
                text=theme,
                variable=self.theme_var,
                value=theme.replace("模式", "").replace(" ", "_").lower()
            )
            rb.pack(anchor=tk.W, padx=20)
        
        # 字体设置
        ttk.Label(frame, text="字体设置:", font=(self.settings["font_family"], 9, "bold")).pack(anchor=tk.W, pady=(20, 5))
        
        font_frame = ttk.Frame(frame)
        font_frame.pack(fill=tk.X)
        
        ttk.Label(font_frame, text="字体大小:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_var = tk.StringVar(value=str(self.settings["font_size"]))
        font_size = ttk.Combobox(font_frame, textvariable=self.font_size_var, width=5)
        font_size['values'] = ("9", "10", "11", "12", "14", "16")
        font_size.pack(side=tk.LEFT)
        
        ttk.Label(font_frame, text="字体:").pack(side=tk.LEFT, padx=(20, 5))
        self.font_family_var = tk.StringVar(value=self.settings["font_family"])
        font_family = ttk.Combobox(font_frame, textvariable=self.font_family_var, width=15)
        font_family['values'] = ("Microsoft YaHei", "SimHei", "SimSun", "Arial", "Verdana", "Tahoma")
        font_family.pack(side=tk.LEFT)
    
    def save_settings(self, settings_window):
        """保存设置并关闭设置窗口"""
        try:
            # 保存常规设置
            self.settings["auto_refresh"] = bool(self.auto_refresh_var.get())
            self.settings["refresh_interval"] = int(self.refresh_interval_var.get())
            
            # 保存平台选择
            self.settings["show_platforms"] = [
                platform for platform, var in self.platform_vars.items() if var.get() == 1
            ]
            
            # 保存通知设置
            self.settings["notify_before"] = int(self.notify_before_var.get())
            
            # 保存界面设置
            self.settings["theme"] = self.theme_var.get()
            self.settings["font_size"] = int(self.font_size_var.get())
            self.settings["font_family"] = self.font_family_var.get()
            
            # 保存开机自启动设置
            new_autostart = bool(self.autostart_var.get())
            if new_autostart != self.settings["autostart"]:
                if set_autostart(new_autostart):
                    self.settings["autostart"] = new_autostart
                else:
                    messagebox.showerror("错误", "设置开机自启动失败，请检查权限")
            
            # 保存到文件
            if self.save_settings_file():
                # 应用新主题
                self.apply_theme(self.settings["theme"])
                
                # 应用新字体
                self.text_area.configure(
                    font=(self.settings["font_family"], self.settings["font_size"])
                )
                
                # 显示保存成功的消息
                messagebox.showinfo("设置已保存", "您的设置已成功保存！")
                
                # 关闭设置窗口
                settings_window.destroy()
            else:
                messagebox.showerror("错误", "保存设置失败，请检查文件权限")
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字")
    
    def save_settings_file(self):
        """保存设置到文件"""
        try:
            config_path = create_config_dir()
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False
    
    def check_queue(self):
        """定期检查队列中的消息"""
        try:
            while True:
                # 尝试获取队列中的消息（非阻塞）
                try:
                    text = self.message_queue.get_nowait()
                    self.add_text(text)
                except queue.Empty:
                    break
        finally:
            # 每100毫秒检查一次队列
            self.root.after(100, self.check_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = OJContestApp(root)
    root.mainloop()