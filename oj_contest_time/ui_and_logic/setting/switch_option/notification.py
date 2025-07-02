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
from plyer import notification

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
    
    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
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
            elif self.os_type == "Darwin":
                return self._schedule_macos(title, contest, message, trigger_time, icon_path)
            elif self.os_type == "Linux":
                return self._schedule_linux(title, contest, message, trigger_time, icon_path)
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
                return self._remove_windows_notifications()
            elif self.os_type == "Darwin":
                return self._remove_macos_notifications()
            elif self.os_type == "Linux":
                return self._remove_linux_notifications()
            else:
                self.logger.warning(f"不支持的操作系统: {self.os_type}")
                return False
        except Exception as e:
            self.logger.error(f"删除通知失败: {e}")
            return False
    
    def _schedule_windows(self, title, contest, message, trigger_time, icon_path):
        """Windows 任务调度实现（增强版）"""
        self.logger.info(f"为Windows创建定时通知: {title}")
        
        # 创建唯一任务ID
        task_id = f"OJNotifier_{int(time.time())}_{contest}"
        
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
            icon_cmd = f"$AppId = 'OJContestNotifier'\n" \
                       f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($toast)"
            app_name_line = f"$AppId = '{self.app_name}'"
        else:
            app_name_line = f"$AppId = '{self.app_name}'"
        
        ps_script = f"""
# 通知参数
$notification = @{{
    Title = "{title}"
    Message = "{formatted_message}"
    AppName = "{self.app_name}"
}}

# 创建通知
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
$xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)
$text = $xml.SelectNodes("//text")
$text[0].AppendChild($xml.CreateTextNode($notification.Title)) | Out-Null
$text[1].AppendChild($xml.CreateTextNode($notification.Message)) | Out-Null

# 设置长持续时间
$toast = $xml.SelectSingleNode("//toast")
if (-not $toast) {{
    $toast = $xml.CreateElement("toast")
    $xml.DocumentElement.AppendChild($toast) | Out-Null
}}
$toast.SetAttribute("duration", "long")

# 创建通知对象
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml

# 显示通知
{app_name_line}
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($toast)

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
            f'schtasks /create /tn "{task_id}" /tr "powershell -ExecutionPolicy Bypass -File {script_path}" '
            f'/sc once /st {time_str} /sd {date_str} /f'
        )
        subprocess.run(command, shell=True, check=True)
        
        self.logger.info(f"已创建Windows定时任务: {task_id}")
        return True
    
    def _remove_windows_notifications(self):
        """删除所有Windows通知任务"""
        self.logger.info("删除所有Windows通知任务...")
        
        # 获取所有任务列表
        result = subprocess.run(
            'schtasks /query /fo list', 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        # 查找所有OJ通知任务
        tasks = []
        for line in result.stdout.splitlines():
            if "任务名" in line and "OJNotifier_" in line:
                task_name = line.split(":")[1].strip()
                tasks.append(task_name)
        
        # 删除找到的任务
        for task in tasks:
            try:
                subprocess.run(f'schtasks /delete /tn "{task}" /f', shell=True, check=True)
                self.logger.info(f"已删除任务: {task}")
            except Exception as e:
                self.logger.error(f"删除任务失败: {task} - {e}")
        
        # 删除临时文件
        self._clean_temp_files()
        
        self.logger.info(f"共删除 {len(tasks)} 个Windows通知任务")
        return True
    
    def _schedule_macos(self, title, contest, message, trigger_time, icon_path):
        """macOS 任务调度实现（增强版）"""
        self.logger.info(f"为macOS创建定时通知: {title}")
        
        # 计算时间戳
        timestamp = int(trigger_time.timestamp())
        task_id = f"com.oj.notification.{timestamp}.{contest}"
        
        # 格式化消息
        formatted_message = self._format_message(message).replace('"', r'\"')
        
        # 创建通知脚本
        script_path = os.path.join(self.temp_dir, f"{task_id}.sh")
        script_content = f"""#!/bin/bash
# 显示通知
osascript -e 'display notification "{formatted_message}" with title "{title}"'

# 任务完成标识
touch "{os.path.join(self.temp_dir, f"{task_id}.done")}"
"""
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        # 创建plist文件
        plist_path = os.path.join(self.temp_dir, f"{task_id}.plist")
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{task_id}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{script_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Minute</key>
        <integer>{trigger_time.minute}</integer>
        <key>Hour</key>
        <integer>{trigger_time.hour}</integer>
        <key>Day</key>
        <integer>{trigger_time.day}</integer>
        <key>Month</key>
        <integer>{trigger_time.month}</integer>
        <key>Year</key>
        <integer>{trigger_time.year}</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        # 复制到LaunchAgents目录
        launch_agents_path = os.path.expanduser("~/Library/LaunchAgents/")
        os.makedirs(launch_agents_path, exist_ok=True)
        dest_plist = os.path.join(launch_agents_path, f"{task_id}.plist")
        shutil.copy(plist_path, dest_plist)
        
        # 加载任务
        subprocess.run(f"launchctl load {dest_plist}", shell=True, check=True)
        
        self.logger.info(f"已创建macOS定时任务: {task_id}")
        return True
    
    def _remove_macos_notifications(self):
        """删除所有macOS通知任务"""
        self.logger.info("删除所有macOS通知任务...")
        
        # LaunchAgents目录
        launch_agents_path = os.path.expanduser("~/Library/LaunchAgents/")
        
        # 查找所有OJ通知任务
        tasks = []
        for filename in os.listdir(launch_agents_path):
            if filename.startswith("com.oj.notification.") and filename.endswith(".plist"):
                task_id = filename[:-6]  # 去掉.plist后缀
                tasks.append(task_id)
        
        # 删除找到的任务
        for task in tasks:
            try:
                plist_path = os.path.join(launch_agents_path, f"{task}.plist")
                
                # 卸载任务
                subprocess.run(f"launchctl unload {plist_path}", shell=True, check=True)
                
                # 删除plist文件
                os.remove(plist_path)
                self.logger.info(f"已删除任务: {task}")
            except Exception as e:
                self.logger.error(f"删除任务失败: {task} - {e}")
        
        # 删除临时文件
        self._clean_temp_files()
        
        self.logger.info(f"共删除 {len(tasks)} 个macOS通知任务")
        return True
    
    def _schedule_linux(self, title, contest, message, trigger_time, icon_path):
        """Linux 任务调度实现（增强版）"""
        self.logger.info(f"为Linux创建定时通知: {title}")
        
        # 创建唯一任务ID
        task_id = f"oj_notifier_{int(time.time())}_{contest}"
        
        # 格式化消息
        formatted_message = self._format_message(message).replace('"', r'\"')
        
        # 图标处理
        icon_cmd = ""
        if icon_path and os.path.exists(icon_path):
            # 复制图标到临时目录
            icon_ext = os.path.splitext(icon_path)[1]
            temp_icon = os.path.join(self.temp_dir, f"{task_id}{icon_ext}")
            shutil.copy(icon_path, temp_icon)
            icon_cmd = f"-i {temp_icon}"
        
        # 创建通知脚本
        script_path = os.path.join(self.temp_dir, f"{task_id}.sh")
        script_content = f"""#!/bin/bash
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

# 显示通知（右侧通知区域）
notify-send -u critical -t 10000 {icon_cmd} "{title}" "{formatted_message}"

# 任务完成标识
touch "{os.path.join(self.temp_dir, f"{task_id}.done")}"
"""
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        # 使用at命令调度任务
        time_str = trigger_time.strftime("%H:%M %Y-%m-%d")
        command = f"echo '{script_path}' | at {time_str}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # 解析任务ID
        match = re.search(r'job (\d+)', result.stdout)
        if not match:
            raise RuntimeError(f"无法解析at任务ID: {result.stdout}")
        
        job_id = match.group(1)
        self.logger.info(f"已创建Linux定时任务: job {job_id}")
        
        # 保存任务ID
        with open(os.path.join(self.temp_dir, f"{task_id}.id"), 'w') as f:
            f.write(job_id)
        
        return True
    
    def _remove_linux_notifications(self):
        """删除所有Linux通知任务"""
        self.logger.info("删除所有Linux通知任务...")
        
        # 获取所有at任务
        result = subprocess.run('atq', shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.logger.error("无法获取at任务列表")
            return False
        
        # 解析任务列表
        tasks = []
        for line in result.stdout.splitlines():
            if line.strip():
                parts = line.split()
                job_id = parts[0]
                tasks.append(job_id)
        
        # 删除所有任务
        count = 0
        for job_id in tasks:
            try:
                # 检查是否是我们创建的任务
                job_info = subprocess.run(
                    f'at -c {job_id}', 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                # 检查是否包含我们的脚本路径
                if self.temp_dir in job_info.stdout:
                    subprocess.run(f'atrm {job_id}', shell=True, check=True)
                    self.logger.info(f"已删除任务: {job_id}")
                    count += 1
            except Exception as e:
                self.logger.error(f"删除任务失败: {job_id} - {e}")
        
        # 删除临时文件
        self._clean_temp_files()
        
        self.logger.info(f"共删除 {count} 个Linux通知任务")
        return True
    
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

# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试使用本地图标（如果有）
    icon_path = None
    for icon_file in ["notification_icon.png", "notification_icon.ico"]:
        test_icon = os.path.join(base_dir, icon_file)
        if os.path.exists(test_icon):
            icon_path = test_icon
            break
    
    nm = NotificationManager("OJ比赛提醒")
    
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        # 清理所有通知
        nm.remove_all_scheduled_notifications()
        print("已清理所有系统通知")
    else:
        # 测试即时通知（带图标）
        nm.show_notification(
            "比赛提醒", 
            "Codeforces Round #789 即将开始！\n时间：2023-05-15 19:35\n持续时间：2小时15分钟", 
            icon_path=icon_path
        )
        
        # 测试系统级定时通知（60秒后触发）
        nm.schedule_system_notification(
            "比赛开始提醒", 
            "CF789",
            "Codeforces Round #789 已经开始！\n请尽快参加比赛！", 
            60,
            icon_path=icon_path
        )
        print("已创建系统级定时通知，将在60秒后触发。现在可以关闭程序。")
        
        # 提示清理命令
        print("\n要清理所有通知，请运行:")
        print(f"python {sys.argv[0]} clean")