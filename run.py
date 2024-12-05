import os
import telebot
from telebot import types
import re
import config
import concurrent.futures
import logging
import subprocess


# 导入 logging 模块
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量，用于存储当前页码
current_page = 0
keyboard = types.InlineKeyboardMarkup()  # 在全局范围内创建键盘对象


# 替换为你的 Telegram bot 的 token
bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def list_namefiles(message):
    # 记录用户的用户名和 ID
    user_info = f"User: {message.from_user.username}, ID: {message.from_user.id}"
    logging.info(user_info)  # 记录到日志中
    with open('userdata.txt', 'a') as userdata_file:
        userdata_file.write(user_info + '\n')  # 保存到 userdata.txt 文件
    bot.send_message(message.chat.id, "我是西瓜皮🍉，\n一个非智能机器人。\n发送 /help 查看帮助！")

 # 处理 /help 命令的函数
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "欢迎使用 \n\n /list - 查看coser列表")

@bot.message_handler(commands=['admin'])
def handle_addlink(message):
    # 调用 1.py 程序
    try:
        subprocess.run(['python', './admin/adminuse.py'], check=True)
        bot.send_message(message.chat.id, "已经启动编辑模式！\n点击 [时空隧道](https://t.me/tgfile2pik_bot) 开始编辑", parse_mode='Markdown')
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"执行 adminuse.py 时出错: {e}")
    
    
# 定义处理 /目录 命令的函数
@bot.message_handler(commands=['list'])
def list_files(message):
    global current_page  # 声明使用全局变量
    global keyboard  # 壮大使用全局变量

    try:
        directory = 'MULU'
        file_list = os.listdir(directory)
        if file_list:
            file_names = [os.path.splitext(file)[0] for file in file_list]  # 只获取文件名部分，不带后缀

            # 重新排列文件名，每页显示4行4列
            rows = []
            current_row = []
            for name in file_names:
                current_row.append(name)
                if len(current_row) == 4:
                    rows.append(current_row)
                    current_row = []
            if current_row:
                rows.append(current_row)

            # 更新当前页码
            if current_page < 0:
                current_page = 0
            if current_page >= len(rows):
                current_page = len(rows) - 1

            # 清空键盘
            keyboard = types.InlineKeyboardMarkup()

            # 创建一个自定义的键盘，根据分页显示文件名
            for row in rows[current_page * 4: current_page * 4 + 4]:  # 根据当前页码显示文件名
                buttons = [types.InlineKeyboardButton(text=name, callback_data=name) for name in row]
                keyboard.row(*buttons)

            # 添加上一页和下一页选项
            if len(rows) > 4:
                prev_button = types.InlineKeyboardButton(text='上一页', callback_data='prev_page')
                next_button = types.InlineKeyboardButton(text='下一页', callback_data='next_page')
                keyboard.row(prev_button, next_button)

            bot.send_message(message.chat.id, '点击选择：', reply_markup=keyboard)
        else:
            bot.reply_to(message, '文件夹为空')
    except Exception as e:
        bot.reply_to(message, f'发生错误：{e}')

# 处理上一页和下一页的回调
@bot.callback_query_handler(func=lambda call: call.data in ['prev_page', 'next_page'])
def page_callback_handler(call):
    global current_page  # 壮大使用全局变量
    if call.data == 'prev_page':
        current_page -= 1  # 切换到上一页
    elif call.data == 'next_page':
        current_page += 1  # 切换到下一页

    list_files(call.message)  # 重新调用列表文件函数，显示更新后的文件列表

# 处理用户点击文件名的回调
@bot.callback_query_handler(func=lambda call: call.data not in ['prev_page', 'next_page'])
def file_callback(call):
    file_name = call.data
    directory = 'MULU'
    file_path = os.path.join(directory, file_name + '.txt')  # 假设所有文件都是文本文件
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            file_content = file.read()
            if file_content.strip():  # 如果文本内容不为空
                if re.match(r'\[.*\]\(.*\)', file_content):  # 如果文本内容是Markdown格式
                    file_content = "```\n" + file_content + "\n```"  # 将文本内容用代码块包裹
                bot.send_message(call.message.chat.id, file_content, parse_mode='Markdown')  
            else:
                bot.send_message(call.message.chat.id, '暂时没有资源，请选择其他选项')
    else:
        bot.send_message(call.message.chat.id, '文件不存在')
# 启动bot
def run_bot():
    logging.info('Bot启动')
    bot.polling()

# 使用多线程
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    executor.submit(run_bot)
