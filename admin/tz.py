# 处理 /delete 命令
@bot.message_handler(commands=['delete'])
def delete_file(message):
    file_list = os.listdir('MULU')
    if file_list:
        markup = telebot.types.InlineKeyboardMarkup(row_width=4)
        buttons = [telebot.types.InlineKeyboardButton(text=os.path.splitext(file)[0], callback_data=file) for file in file_list]
        markup.add(*buttons)
        bot.send_message(message.chat.id, "请选择要删除的文件:", reply_markup=markup)
    else:
        bot.reply_to(message, '文件夹为空')

# 处理用户点击文件名以删除文件
@bot.callback_query_handler(func=lambda call: True)
def delete_file_callback(call):
    file_name = call.data
    file_path = os.path.join('MULU', file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
        bot.send_message(call.message.chat.id, f'{file_name} 已成功删除')
    else:
        bot.send_message(call.message.chat.id, '文件不存在')        
        
