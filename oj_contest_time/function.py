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
from get_information.capture import Main

class all_func:
    def add_text(self, text):
        """添加文本到文本区域"""
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)  # 滚动到底部
    
    def get_today_data(self):
        """获取当天比赛数据"""
        if not self.running:
            self.running = True
            self.status_var.set("状态: 运行中...")
            self.today_button.state(["disabled"])
            self.upcoming_button.state(["disabled"])
            
            # 清空文本区域
            self.text_area.delete(1.0, tk.END)
            self.add_text("开始获取今天的比赛数据...\n")
            
            # 在新线程中运行
            threading.Thread(target=self.run_in_today_thread, daemon=True).start()
    
    def get_upcoming_data(self):
        """获取即将开始比赛数据"""
        if not self.running:
            self.running = True
            self.status_var.set("状态: 运行中...")
            self.today_button.state(["disabled"])
            self.upcoming_button.state(["disabled"])
            
            # 清空文本区域
            self.text_area.delete(1.0, tk.END)
            self.add_text("开始获取即将开始的比赛数据...\n")
            
            # 在新线程中运行
            threading.Thread(target=self.run_in_upcoming_thread, daemon=True).start()
    
    
    def run_in_today_thread(self):
        """在后台线程中获取当天比赛数据"""
        try:
            self.add_text("> 正在获取比赛数据...\n")
            time.sleep(1)  # 模拟网络请求
            
            today_contest = Main.return_today_upcoming_contest()
            self.text_area.delete(1.0, tk.END)
            self.add_text("[OJ_Bot]\n")
            if not today_contest:
                self.add_text("今天没有即将开始的比赛\n")
            else:
                for contest in today_contest:
                    self.add_text("-" * 60 + "\n")
                    self.add_text(f"比赛平台：{contest['platform']}\n")
                    self.add_text(f"比赛链接: {contest['link']}\n")
                    self.add_text(f"比赛标题: {contest['title']}\n")
                    self.add_text(f"比赛时间: {contest['time']}\n")
                    self.add_text(f"比赛时长: {contest['duration']}\n")
            
            self.add_text("> 数据获取完成！\n")
        except Exception as e:
            self.add_text(f"> 错误: {str(e)}\n")
        finally:
            self.running = False
            self.status_var.set("状态: 已停止")
            self.today_button.state(["!disabled"])
            self.upcoming_button.state(["!disabled"])
    
    def run_in_upcoming_thread(self):
        """在后台线程中获取即将开始比赛数据"""
        try:
            self.add_text("> 正在获取比赛数据...\n")
            time.sleep(1)  # 模拟网络请求
            
            upcoming_contest = Main.return_all_upcoming_contest()
            self.text_area.delete(1.0, tk.END)
            self.add_text("[OJ_Bot]\n")
            if not upcoming_contest:
                self.add_text("接下来没有即将开始的比赛\n")
            else:
                for contest in upcoming_contest:
                    self.add_text("-" * 60 + "\n")
                    self.add_text(f"比赛平台：{contest['platform']}\n")
                    self.add_text(f"比赛链接: {contest['link']}\n")
                    self.add_text(f"比赛标题: {contest['title']}\n")
                    self.add_text(f"比赛时间: {contest['time']}\n")
                    self.add_text(f"比赛时长: {contest['duration']}\n")
            
            self.add_text("> 数据获取完成！\n")
        except Exception as e:
            self.add_text(f"> 错误: {str(e)}\n")
        finally:
            self.running = False
            self.status_var.set("状态: 已停止")
            self.today_button.state(["!disabled"])
            self.upcoming_button.state(["!disabled"])
            
    def clear_logs(self):
        """清空日志"""
        self.text_area.delete(1.0, tk.END)
        self.add_text("日志已清空\n")
        self.add_text("等待操作...\n")