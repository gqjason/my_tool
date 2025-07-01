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

class about_system:
    
    def __init__(self):
        pass
    # 获取配置文件路径
    def get_config_path(self):
        if platform.system() == "Windows":
            return os.path.join(os.getenv('APPDATA'), "OJContestApp", "settings.json")
        else:
            return os.path.join(os.path.expanduser("~"), ".config", "OJContestApp", "settings.json")

    # 创建配置目录
    def create_config_dir(self):
        config_path = self.get_config_path()
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return config_path

    # 开机自启动设置
    def set_autostart(self, enable):
        config_path = self.get_config_path()
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