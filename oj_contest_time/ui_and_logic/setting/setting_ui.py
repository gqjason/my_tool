# app/settings_ui.py
import tkinter as tk
from tkinter import ttk, messagebox

class SettingsDialog:
    """设置对话框类"""
    def __init__(self, parent, settings_manager):
        """
        初始化设置对话框
        
        参数:
            parent: 父窗口
            settings_manager: 设置管理类实例
        """
        self.parent = parent
        self.settings_manager = settings_manager

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        
        self.create_setting_widgets()
        self.center_window(self.dialog, parent)
        
        # 应用当前设置到UI
        self.settings_manager.apply_settings(self)
        
        
    def create_setting_widgets(self):
        setting_frame = ttk.Frame(self.dialog)
        setting_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        theme_frame = ttk.LabelFrame(setting_frame, text="主题设置")
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 创建选项卡
        notebook = ttk.Notebook(setting_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(setting_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))       
         
        # 常规设置选项卡
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text="常规设置")
        self.create_general_settings(general_frame)
        
        # 通知设置选项卡
        notify_frame = ttk.Frame(notebook, padding=10)
        notebook.add(notify_frame, text="通知设置")
        self.create_notify_frame(notify_frame)
        
        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.handle_save,
            style="Primary.TButton",
            width=10
        )
        save_button.pack(side=tk.RIGHT, fill=tk.X, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.handle_cancel,
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, fill=tk.X, padx=5)



    def handle_save(self):
        """处理保存按钮点击事件"""
        if self.settings_manager.handle_save(self):
            messagebox.showinfo("成功", "设置已保存并应用")
        else:
            messagebox.showerror("错误", "保存设置失败")
    
    def handle_cancel(self):
        """处理取消按钮点击事件"""
        self.settings_manager.handle_cancel(self.dialog)
    
    def center_window(self, child, parent):
        """
        将子窗口居中显示在父窗口中心
        
        参数:
            child: 子窗口 (Toplevel)
            parent: 父窗口 (Tk 或 Toplevel)
        """
        # 更新窗口尺寸信息
        child.update_idletasks()
        
        # 获取屏幕尺寸
        screen_width = child.winfo_screenwidth()
        screen_height = child.winfo_screenheight()
        
        # 获取父窗口位置和尺寸
        try:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            # 如果父窗口尺寸无效，使用默认值
            if parent_width <= 0:
                parent_width = 800
            if parent_height <= 0:
                parent_height = 600
        except tk.TclError:
            # 如果父窗口已关闭，在屏幕中心显示子窗口
            child_width = child.winfo_width()
            child_height = child.winfo_height()
            x = (screen_width - child_width) // 2
            y = (screen_height - child_height) // 2
            child.geometry(f"+{x}+{y}")
            return
        
        # 获取子窗口尺寸
        child_width = child.winfo_width()
        child_height = child.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - child_width) // 2
        y = parent_y + (parent_height - child_height) // 2
        
        # 确保窗口在屏幕范围内
        if x < 0:
            x = 0
        elif x + child_width > screen_width:
            x = screen_width - child_width
        
        if y < 0:
            y = 0
        elif y + child_height > screen_height:
            y = screen_height - child_height
        
        # 设置窗口位置
        child.geometry(f"+{x}+{y}")
        
    def create_general_settings(self, frame):
        # 开机自启动
        self.autostart_var = tk.BooleanVar(value=self.settings_manager.DEFAULT_SETTINGS["autostart"])
        autostart_check = ttk.Checkbutton(
            frame,
            text="开机自启动",
            variable=self.autostart_var
        )
        autostart_check.pack(anchor="w", pady=2)

        # # 是否最小化到后台运行
        # self.minimize_to_tray_var = tk.BooleanVar(value=self.settings_manager.DEFAULT_SETTINGS["minimize_to_tray"])
        # minimize_to_tray_check = ttk.Checkbutton(
        #     frame,
        #     text="最小化到后台运行",
        #     variable=self.minimize_to_tray_var
        # )
        # minimize_to_tray_check.pack(anchor="w", pady=2)

        # # 开机最小化
        # self.autostart_minimize_var = tk.BooleanVar(value=self.settings_manager.DEFAULT_SETTINGS["autostart_minimize"])
        # autostart_minimize_check = ttk.Checkbutton(
        #     frame,
        #     text="开机时最小化",
        #     variable=self.autostart_minimize_var
        # )
        # autostart_minimize_check.pack(anchor="w", pady=2)
        
    def create_notify_frame(self, frame):
        # 桌面提示选项
        
        self.desktop_notify_var = tk.BooleanVar(value=self.settings_manager.DEFAULT_SETTINGS["desktop_notify"])
        desktop_notify_check = ttk.Checkbutton(
            frame,
            text="启用桌面通知提示\n（将会开启系统定时通知）",
            variable=self.desktop_notify_var
        )
        desktop_notify_check.pack(anchor="w", pady=2)
        

       
        
        
        
    def pr(self, a):
        print(a)