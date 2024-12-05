import os
import telebot
from telebot import types
import config
# 创建一个 Telebot 实例
# bot = telebot.TeleBot("7823106096:AAGuK9s8gO1FNkWyZ67QxKtV38sL9znmX9w")
# 替换为你的 Telegram bot 的 token
bot  = telebot.TeleBot(config.TOKEN)

# 定义状态
TITLE, LINK, FILE_CONTENT = range(3)
# 全局变量，用于存储当前页码
current_page = 0
keyboard = types.InlineKeyboardMarkup()  # 在全局范围内创建键盘对象

# 当收到/addtitle时的处理函数
@bot.message_handler(commands=['addtitle'])
def add_title(message):
    bot.send_message(message.chat.id, "请回复一个标题名:")
    bot.register_next_step_handler(message, process_title_step)

# 处理/addtitle步骤
def process_title_step(message):
    file_name = 'MULU/' + message.text + '.txt'
    with open(file_name, 'w') as file:
        file.write('')
    bot.send_message(message.chat.id, f'{file_name} 创建成功')

# 当收到/addlink时的处理函数
# @bot.message_handler(commands=['addlink'])
# def add_link(message):
 #   file_list = [os.path.splitext(file)[0] for file in os.listdir('MULU')]
    # markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    # buttons = [telebot.types.InlineKeyboardButton(text, callback_data=text) for text in file_list]
    # markup.add(*buttons)
    # bot.send_message(message.chat.id, "请选择文件:", reply_markup=markup)
# 定义处理 /目录 命令的函数
@bot.message_handler(commands=['addlink'])
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

# 处理用户选择的文件
@bot.callback_query_handler(func=lambda call: True)
def process_file_selection(call):
    bot.send_message(call.message.chat.id, f"请输入要写入 {call.data}.txt 的内容:")
    bot.register_next_step_handler(call.message, process_content_step, call.data)

# 处理文件内容步骤
def process_content_step(message, file_name):
    file_name = 'MULU/' + file_name + '.txt'
    with open(file_name, 'a') as file:
        file.write('\n' + message.text)
    bot.send_message(message.chat.id, '内容已保存')

# 启动 bot
bot.polling()
