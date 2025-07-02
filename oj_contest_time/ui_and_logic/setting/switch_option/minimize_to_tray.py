# minimize_to_tray.py
import pystray
from PIL import Image
import threading

class MinimizeToTray:
    def __init__(self, window):
        self.window = window
        self.tray_icon = None
        
    def disable_running(self):
        """禁用最小化到托盘功能"""
        if hasattr(self.window, "protocol"):
            self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        else:
            raise AttributeError("window object does not have 'protocol' method. Make sure to pass a Tkinter window.")

    def enable_running(self):
        """启用最小化到托盘功能"""
        if hasattr(self.window, "protocol"):
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        else:
            raise AttributeError("window object does not have 'protocol' method. Make sure to pass a Tkinter window.")
        
    def on_close(self):
        """窗口关闭事件处理"""
        # 隐藏窗口，实现最小化到托盘
        self.window.withdraw()
        
        # 创建托盘图标
        def on_tray_icon_clicked(icon, item):
            """托盘图标点击事件"""
            self.window.deiconify()
            icon.stop()
            self.tray_icon = None

        # 创建托盘图标
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        icon = pystray.Icon(
            "minimize_to_tray", 
            image, 
            "竞赛提醒工具", 
            menu=pystray.Menu(
                pystray.MenuItem("显示窗口", on_tray_icon_clicked),
                pystray.MenuItem("退出", lambda: self.window.destroy())
            )
        )
        
        # 在单独线程中运行托盘图标
        threading.Thread(target=icon.run, daemon=True).start()
        self.tray_icon = icon