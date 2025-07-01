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
from set_system import about_system

class Setting:
    root = tk.Tk()
    # 设置按钮
    settings_button = ttk.Button(
        root,
        text="⚙️",
        command=about_system.open_settings,
        width=2
    )
    settings_button.pack(side=tk.RIGHT, padx=10)
    
    def save_settings(self):
        """保存设置到文件"""
        config_path = about_system.create_config_dir()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False
    
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
                if about_system.set_autostart(new_autostart):
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