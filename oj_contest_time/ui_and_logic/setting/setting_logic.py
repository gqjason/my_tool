# setting_logic.py
import json
import os
import logging
import platform
from pathlib import Path

from .switch_option.autostarting import AutoStartOption as ASO
from .switch_option.minimize_to_tray import MinimizeToTray as MTT
from ..information.capture import CaptureAllInformation as CAI

class SettingsManager:
    """管理应用程序设置的类"""
    DEFAULT_SETTINGS = {
        "autostart": False,
        "minimize_to_tray": True,
        "autostart_minimize": False,
        "desktop_notify": True,
        "theme": "light",
        "language": "zh_CN"
    }
    
    def __init__(self, config_file="oj_contest_time/other/settings.json"):
        """
        初始化设置管理器
        
        参数:
            config_file: 设置文件路径
        """
        self.config_file = Path(config_file)
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
        
        # 初始化日志
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def load_settings(self):
        """从配置文件加载设置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 合并默认设置和加载的设置
                    for key, value in self.DEFAULT_SETTINGS.items():
                        self.settings[key] = loaded_settings.get(key, value)
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存当前设置到配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(self.config_file.parent, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            self.logger.info("设置已成功保存")
            return True
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False
    
    def get_setting(self, key):
        """获取指定设置项的值"""
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))
    
    def update_setting(self, key, value):
        """更新单个设置项"""
        if key in self.DEFAULT_SETTINGS:
            self.settings[key] = value
            return True
        return False
    
    def update_settings(self, **kwargs):
        """批量更新设置"""
        for key, value in kwargs.items():
            if key in self.DEFAULT_SETTINGS:
                self.settings[key] = value
    
    def apply_settings(self, ui_instance):
        """将设置应用到UI界面"""
        # 更新UI控件状态
        ui_instance.autostart_var.set(self.get_setting("autostart"))
        ui_instance.minimize_to_tray_var.set(self.get_setting("minimize_to_tray"))
        ui_instance.autostart_minimize_var.set(self.get_setting("autostart_minimize"))
        ui_instance.desktop_notify_var.set(self.get_setting("desktop_notify"))
    
    def handle_save(self, ui_instance):
        """处理保存按钮点击事件"""
        # 从UI收集设置值
        settings_data = {
            "autostart": ui_instance.autostart_var.get(),
            "minimize_to_tray": ui_instance.minimize_to_tray_var.get(),
            "autostart_minimize": ui_instance.autostart_minimize_var.get(),
            "desktop_notify": ui_instance.desktop_notify_var.get()
        }
        
        # 更新设置
        self.update_settings(**settings_data)
        
        # 保存到文件
        if self.save_settings():
            # 应用新设置到系统
            self.apply_system_settings()
            return True
        return False
    
    def apply_system_settings(self):
        """将设置应用到操作系统"""
        # 这里可以实现实际的操作系统级设置应用
        # 例如：注册表修改、服务配置等
        self.logger.info("正在应用系统设置...")
        
        # 示例：处理开机自启动
        if self.settings["autostart"]:
            self.logger.info("配置开机自启动...")
            ASO.configure_autostart(True)
        else:
            self.logger.info("禁用开机自启动...")
            ASO.configure_autostart(False)
        
        if self.settings["minimize_to_tray"]:
            self.logger.info("开启最小化到后台运行...")
            MTT.enable_running
        else:
            self.logger.info("关闭最小化到后台运行...")
            MTT.disable_running
            
        
        # 示例：处理通知设置
        if self.settings["desktop_notify"]:
            self.logger.info("启用桌面通知...")
        else:
            self.logger.info("禁用桌面通知...")
    
    def handle_cancel(self, dialog):
        """处理取消按钮点击事件"""
        dialog.destroy()
        
    def switch_system_notification(enable):
        if enable:
            res = CAI.return_today_upcoming_contest()["start_time"]

        