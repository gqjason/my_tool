# app/logic.py
import threading
import time

from .information.capture import Main
from .setting.setting_logic import SettingsManager
class AppLogic:
    
    
    """负责应用程序的核心功能逻辑"""
    def __init__(self, ui_callback=None):
        self.settings_manager = SettingsManager()  # 创建设置管理实例
        self.ui_callback = ui_callback  # UI更新回调函数
        self.running = False
    
    def get_config(self):
        """获取当前配置"""
        return self.settings_manager.get_config()
    
    def save_config(self, new_config):
        """保存新配置"""
        return self.settings_manager.save_config(new_config)
    
    def get_platforms(self):
        """获取监控平台列表"""
        return self.settings_manager.get_platforms()
        
        

    def get_today_data(self):
        """获取当天比赛数据"""
        
        if not self.running:
            self.running = True
            self._update_ui("",True)
            self._update_ui("状态: 运行中...")
            self._update_ui("开始获取今天的比赛数据...\n")

            # 在新线程中运行
            threading.Thread(target=self._get_today_data_thread, daemon=True).start()
    
    def get_upcoming_data(self):
        """获取即将开始比赛数据"""
        
        if not self.running:
            self.running = True
            self._update_ui("",True)
            self._update_ui("状态: 运行中...")
            self._update_ui("开始获取即将开始的比赛数据...\n")

            # 在新线程中运行
            threading.Thread(target=self._get_upcoming_data_thread, daemon=True).start()
    
    def clear_logs(self):
        """清空日志"""
        self._update_ui("clear")  # 特殊指令表示清空日志
    
    def _get_today_data_thread(self):
        """在后台线程中获取当天比赛数据"""
        try:
            self._update_ui("")
            self._update_ui("> 正在获取比赛数据...\n")

            today_contest = Main.return_today_upcoming_contest()
            self._update_ui("[OJ_Bot]\n", clear=True)
            
            if not today_contest:
                self._update_ui("今天没有即将开始的比赛\n")
            else:
                for contest in today_contest:
                    self._update_ui("-" * 60 + "\n")
                    self._update_ui(f"比赛平台：{contest['platform']}\n")
                    self._update_ui(f"比赛链接: {contest['link']}\n")
                    self._update_ui(f"比赛标题: {contest['title']}\n")
                    self._update_ui(f"比赛时间: {contest['time']}\n")
                    self._update_ui(f"比赛时长: {contest['duration']}\n")
            
            self._update_ui("> 数据获取完成！\n")
        except Exception as e:
            self._update_ui(f"> 错误: {str(e)}\n")
        finally:
            self.running = False
            self._update_ui("状态: 已停止")
    
    def _get_upcoming_data_thread(self):
        """在后台线程中获取即将开始比赛数据"""
        try:
            self._update_ui("")
            self._update_ui("> 正在获取比赛数据...\n")

            upcoming_contest = Main.return_all_upcoming_contest()
            self._update_ui("[OJ_Bot]\n", clear=True)
            
            if not upcoming_contest:
                self._update_ui("接下来没有即将开始的比赛\n")
            else:
                for contest in upcoming_contest:
                    self._update_ui("-" * 60 + "\n")
                    self._update_ui(f"比赛平台：{contest['platform']}\n")
                    self._update_ui(f"比赛链接: {contest['link']}\n")
                    self._update_ui(f"比赛标题: {contest['title']}\n")
                    self._update_ui(f"比赛时间: {contest['time']}\n")
                    self._update_ui(f"比赛时长: {contest['duration']}\n")
            
            self._update_ui("> 数据获取完成！\n")
        except Exception as e:
            self._update_ui(f"> 错误: {str(e)}\n")
        finally:
            self.running = False
            self._update_ui("状态: 已停止")
    
    def _update_ui(self, message, clear=False):
        """更新UI界面"""
        if self.ui_callback:
            self.ui_callback(message, clear)