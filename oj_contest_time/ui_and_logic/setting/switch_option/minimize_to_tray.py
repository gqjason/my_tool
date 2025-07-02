import pystray
from PIL import Image
import threading



class MinimizeToTray:
    def __init__(self, window):
        self.window = window
        
    def disable_running(self):
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
    def enable_running(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        # 隐藏窗口，实现最小化到托盘
        self.window.withdraw()
        # 这里可以添加托盘图标相关代码（如pystray等库）

        def on_tray_icon_clicked(icon, item):
            self.window.deiconify()
            icon.stop()

        # 创建一个简单的托盘图标
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        icon = pystray.Icon("minimize_to_tray", image, "My App", menu=pystray.Menu(
            pystray.MenuItem("显示窗口", on_tray_icon_clicked)
        ))
        threading.Thread(target=icon.run, daemon=True).start()
        self.tray_icon = icon   
     
