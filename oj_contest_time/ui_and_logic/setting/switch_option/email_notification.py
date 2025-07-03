import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ssl
import time
from plyer import notification
import socket
import re


class EmailNotificationManager:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email, title, message):
        self.logger = logging.getLogger("EmailNotificationManager")
        self.logger.setLevel(logging.INFO)
        
        # 设置日志处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # 邮件配置
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
        self.title = title
        self.message = message
        # 连接超时设置
        self.timeout = 10  # 秒
        
    def test_smtp_connection(self):
        """测试SMTP服务器连接"""
        try:
            self.logger.info(f"尝试连接到 {self.smtp_server}:{self.smtp_port}...")
            
            # 创建SSL上下文 - 增加兼容性设置
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT@SECLEVEL=1')  # 降低安全级别以兼容更多服务器
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 创建安全连接
            with smtplib.SMTP_SSL(
                self.smtp_server, 
                self.smtp_port, 
                context=context,
                timeout=self.timeout
            ) as server:
                server.noop()  # 发送NOOP命令测试连接
                self.logger.info(f"成功建立SSL连接到 {self.smtp_server}:{self.smtp_port}")
                return True
                
        except (socket.timeout, TimeoutError):
            self.logger.error(f"连接超时: 无法在 {self.timeout} 秒内连接到服务器")
        except ConnectionRefusedError:
            self.logger.error("连接被拒绝: 请检查端口是否正确")
        except ssl.SSLError as e:
            self.logger.error(f"SSL错误: {e}")
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
        return False
    
    def send_email(self, subject, content):
        """发送邮件通知"""
        try:
            # 创建邮件内容
            message = MIMEText(content, 'plain', 'utf-8')
            
            # 修复发件人格式 - 符合RFC5322标准
            # 只使用邮箱地址作为发件人，不使用显示名称
            message['From'] = self.sender_email
            
            # 收件人使用邮箱地址
            message['To'] = self.receiver_email
            
            # 主题使用Header类确保正确编码
            message['Subject'] = Header(subject, 'utf-8')
            
            # 创建兼容的SSL上下文
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT@SECLEVEL=1')
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 使用SMTP_SSL进行安全连接
            with smtplib.SMTP_SSL(
                self.smtp_server, 
                self.smtp_port, 
                context=context,
                timeout=self.timeout
            ) as server:
                # 设置调试级别
                server.set_debuglevel(1)
                
                # 登录服务器
                server.login(self.sender_email, self.sender_password)
                
                # 发送邮件
                server.sendmail(
                    self.sender_email, 
                    self.receiver_email, 
                    message.as_string()
                )
                
            self.logger.info("邮件发送成功")
            return True
            
        except smtplib.SMTPAuthenticationError:
            self.logger.error("认证失败: 请检查邮箱地址和授权码是否正确")
        except smtplib.SMTPServerDisconnected:
            self.logger.error("服务器意外断开连接: 请检查网络连接或服务器状态")
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP协议错误: {e}")
        except (socket.timeout, TimeoutError):
            self.logger.error("操作超时: 请检查网络连接或增加超时时间")
        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
        return False
    
    def show_desktop_notification(self, title, message):
        """显示桌面通知"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="自动通知系统",
                timeout=10
            )
            self.logger.info("桌面通知已发送")
        except Exception as e:
            self.logger.error(f"桌面通知发送失败: {e}")
    
    def go(self):
        """主执行函数"""
        subject = self.title
        content = self.message
        
        # 测试连接
        if not self.test_smtp_connection():
            self.show_desktop_notification("SMTP连接失败", "无法连接到邮件服务器，请检查配置")
            return
        
        # 发送邮件
        if self.send_email(subject, content):
            self.show_desktop_notification("邮件已发送", f"已向{self.receiver_email}发送问候邮件")
        else:
            self.show_desktop_notification("邮件发送失败", "请检查邮件配置和网络连接")

if __name__ == '__main__':
    # 从环境变量获取敏感信息
    ss = "smtp.qq.com"
    sp = 465
    se = "1377592898@qq.com"
    spw = "hbgatafzcuebhcjc"
    rer = "241731627@m.gduf.edu.cn"
    tt = "123"
    ms = "qwer"
    
    # 创建管理器并发送邮件
    manager = EmailNotificationManager(ss, sp, se, spw, rer, tt, ms)
    manager.go()