#!/usr/bin/env python3
import os
import requests
import paramiko
import socket
from datetime import datetime
import pytz
from telegram import Bot
import asyncio
from telegram.error import TelegramError

# # Telegram Bot 设置
# BOT_TOKEN = "YOUR_BOT_TOKEN"
# CHAT_ID = "YOUR_CHAT_ID"

# # 预先定义的常量
# url = '你检测的地址，参考下一行注释'
# # 测试URL 这个URL是个凉了的 url = 'https://edwgiz.serv00.net/'
# ssh_info = {
#     'host': 's3.serv00.com',    # 主机地址
#     'port': 22,
#     'username': '你的用户名',       # 你的用户名，别写错了
#     'password': '你的SSH密码'       # 你注册的时候收到的密码或者你自己改了的密码
# }

# 脚本获取的常量  
url = os.environ.get('URL')  

hostname = os.environ.get('HOSTNAME')
ssh_password = os.environ.get('SSH_PASSWORD')
username = os.environ.get('USERNAME')

ssh_info = {  
    'host': hostname,    # 主机地址
    'port': 22,  
    'username': username,       # 你的用户名，别写错了
    'password': ssh_password      # 你注册的时候收到的密码或者你自己改了的密码
}

# Telegram Bot 设置
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 获取当前脚本文件的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 日志文件将保存在脚本所在的目录中
log_file_path = os.path.join(script_dir, 'Auto_connect_SSH.log')
tg_message_sent = False
flush_log_message = []

# 写入日志的函数
def write_log(log_message):
    global flush_log_message
    if not os.path.exists(log_file_path):
        open(log_file_path, 'a').close()
        os.chmod(log_file_path, 0o644)
    log_info = f"{log_message}"
    flush_log_message.append(log_info)

# 把所有的日志信息写入日志文件
def flush_log():
    global flush_log_message
    username = ssh_info['username']
    system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    beijing_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    current_day = datetime.now(pytz.timezone('Asia/Shanghai')).weekday()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    current_weekday_name = weekdays[current_day]
    flush_log_messages = f"{system_time} - {beijing_time} - {current_weekday_name} - {url} - {username} - {' - '.join(flush_log_message)}"
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(flush_log_messages + '\n')
    flush_log_message.clear()

# 发送Telegram消息的异步函数
async def send_telegram_message_async(message):
    global tg_message_sent
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        tg_status = "Telegram提醒消息发送成功"
        print("温馨提醒：Telegram提醒消息发送成功。")
    except TelegramError as e:
        tg_status = f"Telegram提醒消息发送失败，错误码: {e}"
        print(f"警告：Telegram提醒消息发送失败！\n错误码: {e}")
    finally:
        if not tg_message_sent:
            write_log(f"{tg_status}")
            tg_message_sent = True

# 发送Telegram消息的同步包装函数
def send_telegram_message(message):
    asyncio.run(send_telegram_message_async(message))

# 尝试通过SSH恢复PM2进程的函数  
def restore_pm2_processes():  
    transport = paramiko.Transport((ssh_info['host'], ssh_info['port']))  
    try:  
        transport.connect(username=ssh_info['username'], password=ssh_info['password'])  
        # 创建SSH通道
        ssh = paramiko.SSHClient()  
        ssh._transport = transport  
        try:    # 执行pm2 resurrect命令
            stdin, stdout, stderr = ssh.exec_command('/home/neojinx/.npm-global/bin/pm2 resurrect')  
            print("STDOUT: ", stdout.read().decode())  
            print("STDERR: ", stderr.read().decode())  
            stdout.channel.recv_exit_status()  # 等待命令执行完成
            if stdout.channel.exit_status == 0:
                write_log("通过SSH执行PM2命令成功")
                print("温馨提醒：PM2进程恢复成功。")
            else:
                write_log(f"通过SSH执行PM2命令时出错，错误信息：{stderr.read().decode()}")
                print("警告：PM2进程恢复失败！\n错误信息：", stderr.read().decode())
        except Exception as e:  
            write_log(f"通过SSH执行PM2命令时出错: {e}")
            print(f"通过SSH执行命令时出错: {e}")  
    finally:  
        ssh.close()  # 关闭SSHClient
        transport.close()    # 关闭Transport连接

# 尝试通过SSH连接的函数
def ssh_connect():
    try:
        transport = paramiko.Transport((ssh_info['host'], ssh_info['port']))
        transport.connect(username=ssh_info['username'], password=ssh_info['password'])
        ssh_status = "SSH连接成功"
        print("SSH连接成功。")
    except Exception as e:
        ssh_status = f"SSH连接失败，错误信息: {e}"
        print(f"SSH连接失败: {e}")
    finally:
        transport.close()
        write_log(f"{ssh_status}")

# 检查是否为每月的1号
def is_first_day_of_month():
    return datetime.now().day == 1

# 返回当前的天、月和一年中的第几天
def get_day_info():
    now = datetime.now()
    return now.day, now.month, now.timetuple().tm_yday, ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()]

# 每个月发送仅包含URL和时间的提醒消息
def send_monthly_reminder():
    current_day, current_month, current_year_day, current_weekday_name = get_day_info()
    system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    beijing_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    message = f"🎉每月固定SSH提醒🎉\n-------------------------------------\n检测地址:\n{url}\n-------------------------------------\n　　今天是{current_month}月{current_day}日( {current_weekday_name} )，本月的第 {current_day} 天，今年的第 {current_year_day} 天，例行SSH连接已经成功执行，以防万一空了可以到后台查看记录！\n-------------------------------------\n系统时间: {system_time}\n北京时间: {beijing_time}"
    return message

if __name__ == '__main__':
    # 每月一次检查提醒
    if is_first_day_of_month():
        message = send_monthly_reminder()
        send_telegram_message(message)
        ssh_connect()

    # 检查URL状态和DNS
    try:
        # 尝试解析URL的域名
        host = socket.gethostbyname(url.split('/')[2])
        print(f"解析成功，IP地址为: {host}")
        write_log(f"{host}")

        # 尝试获取URL的状态码
        response = requests.get(url, timeout=10)
        status_code = response.status_code
        if status_code != 200:
            # URL状态码不是200，发送通知并尝试恢复PM2进程
            system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            beijing_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            message = f"💥 当前服务不可用 💥\n地址: {url}\n状态码: {status_code}\n💪 正在尝试通过SSH恢复PM2进程，请稍后手动检查恢复情况！\n-------------------------------------\n系统时间: {system_time}\n北京时间: {beijing_time}"
            write_log(f"主机状态码: {status_code}")
            send_telegram_message(message)
            restore_pm2_processes()
        else:
            write_log(f"主机状态码: {status_code}")
            print(f"主机状态码: {status_code}")

    except socket.gaierror as e:
        # 解析失败，发送通知
        write_log(f"Error: {e}")
        system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        beijing_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        message = f"💣 解析失败提醒 💣\n地址: {url}\n错误: {e}\n😱 抓紧尝试检查解析配置或联系管事的老铁。\n-------------------------------------\n系统时间: {system_time}\n北京时间: {beijing_time}"
        send_telegram_message(message)
        host = "解析失败"
        status_code = "N/A"

    # 添加这些行
    system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    beijing_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    status_message = f"脚本执行完毕\n检测地址: {url}\n解析IP: {host}\n状态码: {status_code}\n系统时间: {system_time}\n北京时间: {beijing_time}"
    send_telegram_message(status_message)

    # 所有日志信息已经收集完成，写入日志文件
    flush_log()
