# notification_manager.py
import os
import platform
import logging
import subprocess
import time
import datetime
import tempfile
import atexit
import re
import shutil
import sys
import json
import threading
import sqlite3
import schedule
import pyautogui
import pyperclip
import pygetwindow as gw
from plyer import notification
import psutil
class NotificationManager:
    """系统通知管理器（支持持久化定时任务和通知清理）"""
    
    def __init__(self, app_name="oj平台比赛查询"):
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 设置日志处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # 检测操作系统
        self.os_type = platform.system()
        self.logger.info(f"初始化通知管理器，操作系统: {self.os_type}")
        
        # 创建临时目录存储相关文件
        self.temp_dir = tempfile.mkdtemp(prefix="oj_notifier_")
        self.logger.info(f"创建临时目录: {self.temp_dir}")
        
        # 注册退出清理函数
        atexit.register(self.cleanup)
        
        # 存储任务ID用于清理
        self.scheduled_tasks = {
            "windows": [],
            "macos": [],
            "linux": []
        }
        self._load_scheduled_tasks()
    
    def _load_scheduled_tasks(self):
        """加载之前保存的任务ID"""
        task_file = os.path.join(self.temp_dir, "scheduled_tasks.json")
        if os.path.exists(task_file):
            try:
                with open(task_file, 'r') as f:
                    self.scheduled_tasks = json.load(f)
                self.logger.info(f"已加载 {len(self.scheduled_tasks['windows'] + self.scheduled_tasks['macos'] + self.scheduled_tasks['linux'])} 个计划任务")
            except Exception as e:
                self.logger.error(f"加载计划任务失败: {e}")
    
    def _save_scheduled_tasks(self):
        """保存任务ID到文件"""
        task_file = os.path.join(self.temp_dir, "scheduled_tasks.json")
        try:
            with open(task_file, 'w') as f:
                json.dump(self.scheduled_tasks, f)
        except Exception as e:
            self.logger.error(f"保存计划任务失败: {e}")
    
    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                # 保存任务ID以便下次加载
                self._save_scheduled_tasks()
                
                # 不要删除整个目录，只清理临时文件
                for filename in os.listdir(self.temp_dir):
                    if filename != "scheduled_tasks.json":
                        file_path = os.path.join(self.temp_dir, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                self.logger.info(f"已清理临时目录: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"清理临时目录失败: {e}")
    
    def show_notification(self, title, message, duration=10, icon_path=None):
        """
        显示系统通知（增强版）
        
        参数:
            title: 通知标题
            message: 通知内容（支持多行）
            duration: 通知显示时间（秒），默认10秒
            icon_path: 自定义图标路径
        """
        try:
            # 格式化消息（确保多行显示）
            formatted_message = self._format_message(message)
            
            # 设置通知参数
            kwargs = {
                "title": title,
                "message": formatted_message,
                "app_name": self.app_name,
                "timeout": duration
            }
            
            # 添加图标（如果可用）
            if icon_path and os.path.exists(icon_path):
                kwargs["app_icon"] = icon_path
                self.logger.info(f"使用自定义图标: {icon_path}")
            
            notification.notify(**kwargs)
            self.logger.info(f"已发送通知: {title}")
            return True
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            return False
    
    def _format_message(self, message):
        """格式化通知消息，确保多行显示"""
        # 添加换行符确保多行显示
        if isinstance(message, list):
            return "\n".join(message)
        if "\n" not in message and len(message) > 50:
            # 在适当位置添加换行符
            parts = message.split("，")
            if len(parts) > 1:
                return "，\n".join(parts)
        return message
    
    def schedule_system_notification(self, title, contest, message, delay_seconds, icon_path=None):
        """
        将定时通知注入系统任务调度器
        即使程序关闭后也能触发通知
        
        参数:
            title: 通知标题
            contest: 比赛标识（用于创建唯一任务ID）
            message: 通知内容
            delay_seconds: 延迟时间（秒）
            icon_path: 自定义图标路径
        """
        try:
            # 计算触发时间
            trigger_time = datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)
            
            if self.os_type == "Windows":
                return self._schedule_windows(title, contest, message, trigger_time, icon_path)
            # elif self.os_type == "Darwin":
            #     return self._schedule_macos(title, contest, message, trigger_time, icon_path)
            # elif self.os_type == "Linux":
            #     return self._schedule_linux(title, contest, message, trigger_time, icon_path)
            else:
                self.logger.warning(f"不支持的操作系统: {self.os_type}")
                return False
        except Exception as e:
            self.logger.error(f"创建系统定时任务失败: {e}")
            return False
    
    def remove_all_scheduled_notifications(self):
        """
        删除所有由本程序创建的系统通知
        """
        try:
            self.logger.info("开始删除所有计划的通知...")
            if self.os_type == "Windows":
                success = self._remove_windows_notifications()
            elif self.os_type == "Darwin":
                success = self._remove_macos_notifications()
            elif self.os_type == "Linux":
                success = self._remove_linux_notifications()
            else:
                self.logger.warning(f"不支持的操作系统: {self.os_type}")
                return False
            
            # 清除任务列表
            self.scheduled_tasks = {"windows": [], "macos": [], "linux": []}
            self._save_scheduled_tasks()
            
            return success
        except Exception as e:
            self.logger.error(f"删除通知失败: {e}")
            return False
    
    def _schedule_windows(self, title, contest, message, trigger_time, icon_path):
        """Windows 任务调度实现（增强版）"""
        self.logger.info(f"为Windows创建定时通知: {title}")
        
        # 创建唯一任务ID
        task_id = f"OJNotifier_{int(time.time())}_{contest}"
        
        # 添加到任务列表
        self.scheduled_tasks["windows"].append(task_id)
        self._save_scheduled_tasks()
        
        # 格式化消息
        formatted_message = self._format_message(message).replace('"', '""')
        
        # 创建PowerShell脚本
        script_path = os.path.join(self.temp_dir, f"{task_id}.ps1")
        
        # 图标处理
        icon_cmd = ""
        if icon_path and os.path.exists(icon_path):
            # 复制图标到临时目录
            icon_ext = os.path.splitext(icon_path)[1]
            temp_icon = os.path.join(self.temp_dir, f"{task_id}{icon_ext}")
            shutil.copy(icon_path, temp_icon)
            icon_cmd = f"$AppId = 'OJContestNotifier'"
        else:
            icon_cmd = f"$AppId = '{self.app_name}'"
        
        ps_script = f"""
# 通知参数
$notification = @{{
    Title = "{title}"
    Message = "{formatted_message}"
}}

# 加载程序集
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 创建通知窗口
$form = New-Object System.Windows.Forms.Form
$form.Text = $notification.Title
$form.Size = New-Object System.Drawing.Size(300, 150)
$form.StartPosition = "Manual"
$form.FormBorderStyle = "FixedDialog"
$form.TopMost = $true

# 设置位置到右下角
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$workArea = $screen.WorkingArea
$form.Location = New-Object System.Drawing.Point(($workArea.Width - $form.Width), ($workArea.Height - $form.Height))

# 添加内容
$label = New-Object System.Windows.Forms.Label
$label.Location = New-Object System.Drawing.Point(10, 20)
$label.Size = New-Object System.Drawing.Size(280, 80)
$label.Text = $notification.Message
$label.Font = New-Object System.Drawing.Font("Microsoft YaHei", 10)
$form.Controls.Add($label)

# 添加图标
if (Test-Path "{icon_path}") {{
    $icon = New-Object System.Drawing.Icon ("{icon_path}")
    $form.Icon = $icon
}}

# 显示通知
$form.Show()

# 自动关闭计时器
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 10000  # 10秒
$timer.Add_Tick({{ $form.Close(); $timer.Stop() }})
$timer.Start()

# 进入消息循环
[System.Windows.Forms.Application]::DoEvents()

# 任务完成标识
Set-Content -Path "{os.path.join(self.temp_dir, f"{task_id}.done")}" -Value "Completed"
"""
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        # 格式化为Windows任务计划要求的格式
        time_str = trigger_time.strftime("%H:%M")
        date_str = trigger_time.strftime("%Y/%m/%d")
        
        # 创建一次性任务
        command = (
            f'schtasks /create /tn "{task_id}" /tr "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File {script_path}" '
            f'/sc once /st {time_str} /sd {date_str} /f'
        )
        subprocess.run(command, shell=True, check=True)
        
        self.logger.info(f"已创建Windows定时任务: {task_id}")
        return True
    
    def _remove_windows_notifications(self):
        """删除所有Windows通知任务"""
        self.logger.info("删除所有Windows通知任务...")
        
        # 从任务列表获取任务
        tasks = self.scheduled_tasks["windows"][:]
        
        # 删除找到的任务
        for task in tasks:
            try:
                subprocess.run(f'schtasks /delete /tn "{task}" /f', shell=True, check=True)
                self.logger.info(f"已删除任务: {task}")
                
                # 从任务列表中移除
                if task in self.scheduled_tasks["windows"]:
                    self.scheduled_tasks["windows"].remove(task)
            except Exception as e:
                self.logger.error(f"删除任务失败: {task} - {e}")
        
        # 删除临时文件
        self._clean_temp_files()
        
        self.logger.info(f"共删除 {len(tasks)} 个Windows通知任务")
        return True
    
#     def _schedule_macos(self, title, contest, message, trigger_time, icon_path):
#         """macOS 任务调度实现（增强版）"""
#         self.logger.info(f"为macOS创建定时通知: {title}")
        
#         # 计算时间戳
#         timestamp = int(trigger_time.timestamp())
#         task_id = f"com.oj.notification.{timestamp}.{contest}"
        
#         # 添加到任务列表
#         self.scheduled_tasks["macos"].append(task_id)
#         self._save_scheduled_tasks()
        
#         # 格式化消息
#         formatted_message = self._format_message(message).replace('"', r'\"')
        
#         # 创建通知脚本
#         script_path = os.path.join(self.temp_dir, f"{task_id}.sh")
        
#         # 图标处理
#         icon_cmd = ""
#         if icon_path and os.path.exists(icon_path):
#             # 复制图标到临时目录
#             icon_ext = os.path.splitext(icon_path)[1]
#             temp_icon = os.path.join(self.temp_dir, f"{task_id}{icon_ext}")
#             shutil.copy(icon_path, temp_icon)
#             icon_cmd = f'-contentImage "{temp_icon}"'
        
#         script_content = f"""#!/bin/bash
# # 显示通知
# osascript -e 'display notification "{formatted_message}" with title "{title}" {icon_cmd}'

# # 任务完成标识
# touch "{os.path.join(self.temp_dir, f"{task_id}.done")}"
# """
#         with open(script_path, 'w') as f:
#             f.write(script_content)
#         os.chmod(script_path, 0o755)
        
#         # 创建plist文件
#         plist_path = os.path.join(self.temp_dir, f"{task_id}.plist")
#         plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
# <plist version="1.0">
# <dict>
#     <key>Label</key>
#     <string>{task_id}</string>
#     <key>ProgramArguments</key>
#     <array>
#         <string>{script_path}</string>
#     </array>
#     <key>StartCalendarInterval</key>
#     <dict>
#         <key>Minute</key>
#         <integer>{trigger_time.minute}</integer>
#         <key>Hour</key>
#         <integer>{trigger_time.hour}</integer>
#         <key>Day</key>
#         <integer>{trigger_time.day}</integer>
#         <key>Month</key>
#         <integer>{trigger_time.month}</integer>
#         <key>Year</key>
#         <integer>{trigger_time.year}</integer>
#     </dict>
#     <key>RunAtLoad</key>
#     <false/>
# </dict>
# </plist>
# """
#         with open(plist_path, 'w') as f:
#             f.write(plist_content)
        
#         # 复制到LaunchAgents目录
#         launch_agents_path = os.path.expanduser("~/Library/LaunchAgents/")
#         os.makedirs(launch_agents_path, exist_ok=True)
#         dest_plist = os.path.join(launch_agents_path, f"{task_id}.plist")
#         shutil.copy(plist_path, dest_plist)
        
#         # 加载任务
#         subprocess.run(f"launchctl load {dest_plist}", shell=True, check=True)
        
#         self.logger.info(f"已创建macOS定时任务: {task_id}")
#         return True
    
#     def _remove_macos_notifications(self):
#         """删除所有macOS通知任务"""
#         self.logger.info("删除所有macOS通知任务...")
        
#         # LaunchAgents目录
#         launch_agents_path = os.path.expanduser("~/Library/LaunchAgents/")
        
#         # 查找所有OJ通知任务
#         tasks = self.scheduled_tasks["macos"][:]
        
#         # 删除找到的任务
#         for task in tasks:
#             try:
#                 plist_path = os.path.join(launch_agents_path, f"{task}.plist")
                
#                 # 卸载任务
#                 subprocess.run(f"launchctl unload {plist_path}", shell=True, check=True)
                
#                 # 删除plist文件
#                 os.remove(plist_path)
#                 self.logger.info(f"已删除任务: {task}")
                
#                 # 从任务列表中移除
#                 if task in self.scheduled_tasks["macos"]:
#                     self.scheduled_tasks["macos"].remove(task)
#             except Exception as e:
#                 self.logger.error(f"删除任务失败: {task} - {e}")
        
#         # 删除临时文件
#         self._clean_temp_files()
        
#         self.logger.info(f"共删除 {len(tasks)} 个macOS通知任务")
#         return True
    
#     def _schedule_linux(self, title, contest, message, trigger_time, icon_path):
#         """Linux 任务调度实现（增强版）"""
#         self.logger.info(f"为Linux创建定时通知: {title}")
        
#         # 创建唯一任务ID
#         task_id = f"oj_notifier_{int(time.time())}_{contest}"
        
#         # 添加到任务列表
#         self.scheduled_tasks["linux"].append(task_id)
#         self._save_scheduled_tasks()
        
#         # 格式化消息
#         formatted_message = self._format_message(message).replace('"', r'\"')
        
#         # 图标处理
#         icon_cmd = ""
#         if icon_path and os.path.exists(icon_path):
#             # 复制图标到临时目录
#             icon_ext = os.path.splitext(icon_path)[1]
#             temp_icon = os.path.join(self.temp_dir, f"{task_id}{icon_ext}")
#             shutil.copy(icon_path, temp_icon)
#             icon_cmd = f"-i {temp_icon}"
        
#         # 创建通知脚本
#         script_path = os.path.join(self.temp_dir, f"{task_id}.sh")
#         script_content = f"""#!/bin/bash
# export DISPLAY=:0
# export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

# # 显示通知（右侧通知区域）
# notify-send -u critical -t 10000 {icon_cmd} "{title}" "{formatted_message}"

# # 任务完成标识
# touch "{os.path.join(self.temp_dir, f"{task_id}.done")}"
# """
#         with open(script_path, 'w') as f:
#             f.write(script_content)
#         os.chmod(script_path, 0o755)
        
#         # 使用at命令调度任务
#         time_str = trigger_time.strftime("%H:%M %Y-%m-%d")
#         command = f"echo '{script_path}' | at {time_str}"
#         result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
#         # 解析任务ID
#         match = re.search(r'job (\d+)', result.stdout)
#         if not match:
#             raise RuntimeError(f"无法解析at任务ID: {result.stdout}")
        
#         job_id = match.group(1)
#         self.logger.info(f"已创建Linux定时任务: job {job_id}")
        
#         # 保存任务ID
#         with open(os.path.join(self.temp_dir, f"{task_id}.id"), 'w') as f:
#             f.write(job_id)
        
#         return True
    
#     def _remove_linux_notifications(self):
#         """删除所有Linux通知任务"""
#         self.logger.info("删除所有Linux通知任务...")
        
#         # 获取所有at任务
#         result = subprocess.run('atq', shell=True, capture_output=True, text=True)
#         if result.returncode != 0:
#             self.logger.error("无法获取at任务列表")
#             return False
        
#         # 解析任务列表
#         tasks = []
#         for line in result.stdout.splitlines():
#             if line.strip():
#                 parts = line.split()
#                 job_id = parts[0]
#                 tasks.append(job_id)
        
#         # 删除所有任务
#         count = 0
#         for job_id in tasks:
#             try:
#                 # 检查是否是我们创建的任务
#                 job_info = subprocess.run(
#                     f'at -c {job_id}', 
#                     shell=True, 
#                     capture_output=True, 
#                     text=True
#                 )
                
#                 # 检查是否包含我们的脚本路径
#                 if self.temp_dir in job_info.stdout:
#                     subprocess.run(f'atrm {job_id}', shell=True, check=True)
#                     self.logger.info(f"已删除任务: {job_id}")
#                     count += 1
#             except Exception as e:
#                 self.logger.error(f"删除任务失败: {job_id} - {e}")
        
#         # 删除临时文件
#         self._clean_temp_files()
        
#         # 清空任务列表
#         self.scheduled_tasks["linux"] = []
#         self._save_scheduled_tasks()
        
#         self.logger.info(f"共删除 {count} 个Linux通知任务")
#         return True
    
    def _clean_temp_files(self):
        """清理临时目录中的完成标记文件"""
        try:
            for filename in os.listdir(self.temp_dir):
                if filename.endswith(".done") or filename.endswith(".id") or filename.endswith(".png") or filename.endswith(".ico"):
                    os.remove(os.path.join(self.temp_dir, filename))
            self.logger.info("已清理临时标记文件")
        except Exception as e:
            self.logger.error(f"清理临时文件失败: {e}")
    
    def is_notification_enabled(self):
        """检查系统通知是否启用（跨平台）"""
        # Windows
        if self.os_type == "Windows":
            try:
                import winreg

                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings") as key:
                    enabled = winreg.QueryValueEx(key, "NOC_GLOBAL_SETTING_TOASTS_ENABLED")[0]
                    return bool(enabled)
            except:
                return True
        
        # macOS
        elif self.os_type == "Darwin":
            # 检查通知中心是否启用
            try:
                result = subprocess.run(
                    "defaults read com.apple.notificationcenterui", 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                return "dndStart" not in result.stdout
            except:
                return True
        
        # Linux
        elif self.os_type == "Linux":
            # 检查是否安装了通知服务器
            return os.system("which notify-send") == 0
        
        return True

class WeChatNotificationManager:
    """微信通知管理器（使用PyAutoGUI发送消息）"""
    
    def __init__(self, db_path="wechat_groups.db"):
        self.logger = logging.getLogger("WeChatManager")
        self.logger.setLevel(logging.INFO)
        
        # 设置日志处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # 初始化数据库
        self.db_path = db_path
        self._init_database()
        
        # 微信窗口标题（根据语言可能不同）
        self.wechat_titles = ["微信", "微信(Windows)"]
        
        # 启动定时任务线程
        self.running = True
        self.thread = threading.Thread(target=self._schedule_thread)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("微信通知管理器初始化完成")
    
    def _init_database(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wechat_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL UNIQUE,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                message TEXT NOT NULL,
                send_time TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'scheduled'  -- scheduled, sent, failed
            )
        ''')
        self.conn.commit()
        self.logger.info(f"数据库初始化完成: {self.db_path}")
    
    def _schedule_thread(self):
        """定时任务线程"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def is_wechat_running(self):
        """检查微信是否在运行"""
        try:
            for title in self.wechat_titles:
                if gw.getWindowsWithTitle(title):
                    return True
                
            return False
        except Exception as e:
            self.logger.error(f"检查微信运行状态失败: {e}")
            return False
    
    def activate_wechat(self):
        """激活微信窗口"""
        try:
            for title in self.wechat_titles:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    win = windows[0]
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    time.sleep(1)  # 等待窗口激活
                    return True
            return False
        except Exception as e:
            self.logger.error(f"激活微信窗口失败: {e}")
            return False
    
    def search_group(self, group_name):
        """搜索微信群"""
        try:
            # 激活微信窗口
            if not self.activate_wechat():
                self.logger.error("无法激活微信窗口")
                return False
            
            # 按Ctrl+F打开搜索框
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.2)
            
            # 清空搜索框内容（多次退格，确保干净）
            for _ in range(30):
                pyautogui.press('backspace')
            time.sleep(0.2)
            # 粘贴群名称（更兼容中文/特殊字符）
            pyperclip.copy(group_name)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)  # 等待搜索结果
            
            # 按Enter选择第一个结果
            pyautogui.press('enter')
            time.sleep(1)  # 等待进入群聊
            
            # 点击输入框（假设输入框在窗口底部，向下移动一定像素）
            win = gw.getWindowsWithTitle(self.wechat_titles[0])[0]
            x, y, w, h = win.left, win.top, win.width, win.height
            pyautogui.click(x + w // 2, y + h - 50)
            time.sleep(0.5)
            # 检查是否成功进入群聊
            # 这里可以添加一些检查逻辑，比如检查窗口标题等
            return True
        except Exception as e:
            self.logger.error(f"搜索微信群失败: {e}")
            return False
    
    def add_wechat_group(self, group_name):
        """添加微信群到数据库"""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO wechat_groups (group_name) VALUES (?)",
                (group_name,)
            )
            self.conn.commit()
            self.logger.info(f"已添加/更新微信群: {group_name}")
            return True
        except Exception as e:
            self.logger.error(f"添加微信群失败: {e}")
            return False
    
    def get_wechat_groups(self):
        """获取所有微信群"""
        try:
            self.cursor.execute("SELECT group_name FROM wechat_groups ORDER BY last_used DESC")
            groups = [row[0] for row in self.cursor.fetchall()]
            return groups
        except Exception as e:
            self.logger.error(f"获取微信群失败: {e}")
            return []
    
    def schedule_wechat_message(self, group_name, message, send_time):
        """
        安排定时微信消息
        
        参数:
            group_name: 微信群名称
            message: 要发送的消息
            send_time: 发送时间 (datetime对象)
        """
        try:
            # 计算延迟时间（秒）
            now = datetime.datetime.now()
            delay_seconds = (send_time - now).total_seconds()
            
            if delay_seconds <= 0:
                self.logger.warning("发送时间必须在未来")
                return False
            
            # 添加到数据库
            self.cursor.execute(
                "INSERT INTO scheduled_messages (group_name, message, send_time) VALUES (?, ?, ?)",
                (group_name, message, send_time.strftime("%Y-%m-%d %H:%M:%S"))
            )
            self.conn.commit()
            
            # 安排任务
            schedule.every(delay_seconds).seconds.do(
                self._send_wechat_message, 
                group_name, 
                message,
                self.cursor.lastrowid
            )
            
            self.logger.info(f"已安排微信消息: {group_name} 在 {send_time}")
            return True
        except Exception as e:
            self.logger.error(f"安排微信消息失败: {e}")
            return False
    
    def _send_wechat_message(self, group_name, message, message_id=None):
        """发送微信消息"""
        try:
            # 检查微信是否运行
            if not self.is_wechat_running():
                self.logger.warning("微信客户端未运行，无法发送消息")
                if message_id:
                    self.cursor.execute(
                        "UPDATE scheduled_messages SET status = 'failed' WHERE id = ?",
                        (message_id,)
                    )
                    self.conn.commit()
                return False
            
            # 搜索并进入群聊
            if not self.search_group(group_name):
                self.logger.error(f"无法找到群聊: {group_name}")
                if message_id:
                    self.cursor.execute(
                        "UPDATE scheduled_messages SET status = 'failed' WHERE id = ?",
                        (message_id,)
                    )
                    self.conn.commit()
                return False
            
            # 发送消息
            try:
                pyperclip.copy(message)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.2)
                pyautogui.press('enter')
                # 分割长消息为多行

                self.logger.info(f"已发送微信消息到: {group_name}")
                
                # 更新最近使用时间
                self.cursor.execute(
                    "UPDATE wechat_groups SET last_used = CURRENT_TIMESTAMP WHERE group_name = ?",
                    (group_name,)
                )
                
                # 标记为已发送
                if message_id:
                    self.cursor.execute(
                        "UPDATE scheduled_messages SET status = 'sent' WHERE id = ?",
                        (message_id,)
                    )
                
                self.conn.commit()
                return True
            except Exception as e:
                self.logger.error(f"发送消息时出错: {e}")
                if message_id:
                    self.cursor.execute(
                        "UPDATE scheduled_messages SET status = 'failed' WHERE id = ?",
                        (message_id,)
                    )
                    self.conn.commit()
                return False
        except Exception as e:
            self.logger.error(f"发送微信消息失败: {e}")
            if message_id:
                self.cursor.execute(
                    "UPDATE scheduled_messages SET status = 'failed' WHERE id = ?",
                    (message_id,)
                )
                self.conn.commit()
            return False
    
    def load_scheduled_messages(self):
        """加载数据库中的定时消息"""
        try:
            self.cursor.execute("SELECT id, group_name, message, send_time FROM scheduled_messages WHERE status = 'scheduled'")
            messages = self.cursor.fetchall()
            
            for msg_id, group_name, message, send_time in messages:
                # 转换时间字符串为datetime
                send_time = datetime.datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")
                
                # 计算延迟时间（秒）
                now = datetime.datetime.now()
                delay_seconds = (send_time - now).total_seconds()
                
                if delay_seconds > 0:
                    # 安排任务
                    schedule.every(delay_seconds).seconds.do(
                        self._send_wechat_message, 
                        group_name, 
                        message,
                        msg_id
                    )
                    self.logger.info(f"已加载定时消息: {group_name} 在 {send_time}")
                else:
                    # 标记为过期
                    self.cursor.execute(
                        "UPDATE scheduled_messages SET status = 'failed' WHERE id = ?",
                        (msg_id,)
                    )
                    self.logger.info(f"已标记过期消息: {group_name}")
            
            self.conn.commit()
            return len(messages)
        except Exception as e:
            self.logger.error(f"加载定时消息失败: {e}")
            return 0
    
    def shutdown(self):
        """关闭管理器"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=5)
        self.conn.close()
        self.logger.info("微信通知管理器已关闭")


class NotificationSystem:
    """完整的通知系统（整合系统通知和微信通知）"""
    
    def __init__(self):
        # 初始化系统通知管理器
        self.system_notifier = NotificationManager()
        
        # 初始化微信通知管理器
        self.wechat_manager = WeChatNotificationManager()
        
        # 加载已有的定时消息
        self.wechat_manager.load_scheduled_messages()
        
        # 注册退出处理
        atexit.register(self.shutdown)
    
    def is_wechat_running(self):
        """检查微信是否在运行"""
        return self.wechat_manager.is_wechat_running()
    
    def send_desktop_notification(self, title, message, duration=10, icon_path=None):
        """发送桌面通知"""
        return self.system_notifier.show_notification(title, message, duration, icon_path)
    
    def schedule_desktop_notification(self, title, contest, message, delay_seconds, icon_path=None):
        """安排定时桌面通知"""
        return self.system_notifier.schedule_system_notification(
            title, contest, message, delay_seconds, icon_path
        )
    
    def add_wechat_group(self, group_name):
        """添加微信群"""
        return self.wechat_manager.add_wechat_group(group_name)
    
    def get_wechat_groups(self):
        """获取所有微信群"""
        return self.wechat_manager.get_wechat_groups()
    
    def send_wechat_message(self, group_name, message):
        """立即发送微信消息"""
        return self.wechat_manager._send_wechat_message(group_name, message, None)
    
    def schedule_wechat_message(self, group_name, message, send_time):
        """安排定时微信消息"""
        return self.wechat_manager.schedule_wechat_message(group_name, message, send_time)
    
    def shutdown(self):
        """关闭系统"""
        self.wechat_manager.shutdown()
        self.system_notifier.cleanup()


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建通知系统
    notifier = NotificationSystem()
    
    # 测试桌面通知
    notifier.send_desktop_notification(
        "系统测试", 
        "这是一个桌面通知测试！"
    )
    
    # 安排定时桌面通知（60秒后）
    # notifier.schedule_desktop_notification(
    #     "定时通知测试", 
    #     "test_event",
    #     "这是一个定时桌面通知测试，将在60秒后显示！",
    #     60
    # )
    
    # 添加微信群
    group_name = "信息测试"  # 替换为实际的微信群名称
    notifier.add_wechat_group(group_name)
    
    # 检查微信是否运行
    if notifier.is_wechat_running():
        # 测试立即发送微信消息
        notifier.send_wechat_message(
            group_name,
            "这是一条测试微信消息！"
        )
        
        # 安排定时微信消息（120秒后）
        send_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
        notifier.schedule_wechat_message(
            group_name,
            "这是一条定时微信消息，将在2分钟后发送！",
            send_time
        )
    else:
        logging.warning("微信客户端未运行，跳过微信通知测试")
    
    print("所有通知已安排，按Ctrl+C退出程序...")
    
    try:
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序已退出")