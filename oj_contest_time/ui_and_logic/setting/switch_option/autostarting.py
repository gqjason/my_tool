import winreg
import sys
import platform
import os
import plistlib
class AutoStartOption:
    def __init__(self):
        # If you have a logger, assign it here. Otherwise, use print as fallback.
        self.logger = None

    def configure_autostart(self, enable):
        """配置开机自启动（跨平台实现）"""
        os_type = platform.system()
        print(os_type)
        try:
            if os_type == "Windows":
                self._configure_windows_autostart(enable)
            elif os_type == "Darwin":  # macOS
                self._configure_macos_autostart(enable)
            elif os_type == "Linux":
                self._configure_linux_autostart(enable)
        except Exception as e:
            print("unsuccess!")
                 
                
    def _configure_windows_autostart(self, enable):
        """Windows开机自启动配置"""

        # 获取当前可执行文件路径
        exe_path = sys.executable
        
        # 注册表路径
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "CaptureOJContestTime"
        
        if enable:
            # 创建注册表项，如果不存在则创建
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            with key:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
            if self.logger:
                self.logger.info("Windows开机自启动已启用")
            else:
                print("Windows开机自启动已启用")
        else:
            # 删除注册表项
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, app_name)
                if self.logger:
                    self.logger.info("Windows开机自启动已禁用")
                else:
                    print("Windows开机自启动已禁用")
            except FileNotFoundError:
                pass  # 如果键不存在，忽略错误
            # 删除注册表项
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.DeleteValue(key, app_name)
                self.logger.info("Windows开机自启动已禁用")
            except FileNotFoundError:
                pass  # 如果键不存在，忽略错误
    
    def _configure_macos_autostart(self, enable):
        """macOS开机自启动配置"""
        # 获取当前可执行文件路径
        if self.logger:
            self.logger.info(f"macOS开机自启动 {'已启用' if enable else '已禁用'}")
        else:
            print(f"macOS开机自启动 {'已启用' if enable else '已禁用'}")
        label = "com.myapp.autostart"
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
        exe_path = sys.executable
        if enable:
            plist_content = {
            "Label": label,
            "ProgramArguments": [exe_path, "--minimized"],
            "RunAtLoad": True,
            "KeepAlive": False,
            }
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            with open(plist_path, "wb") as f:
                plistlib.dump(plist_content, f)
        else:
            if os.path.exists(plist_path):
                os.remove(plist_path)
        self.logger.info(f"macOS开机自启动 {'已启用' if enable else '已禁用'}")
    
    def _configure_linux_autostart(self, enable):
        """Linux开机自启动配置"""
        # 在Linux上，通常需要创建.desktop文件

        if self.logger:
            self.logger.info(f"Linux开机自启动 {'已启用' if enable else '已禁用'}")
        else:
            print(f"Linux开机自启动 {'已启用' if enable else '已禁用'}")
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_file = os.path.join(autostart_dir, "myapp-autostart.desktop")
        exe_path = sys.executable

        if enable:
            desktop_content = f"""[Desktop Entry]
    Type=Application
    Exec={exe_path} --minimized
    Hidden=false
    NoDisplay=false
    X-GNOME-Autostart-enabled=true
    Name=MyApp
    Comment=Start MyApp on login
    """
            with open(desktop_file, "w") as f:
                f.write(desktop_content)
        else:
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
        self.logger.info(f"Linux开机自启动 {'已启用' if enable else '已禁用'}")