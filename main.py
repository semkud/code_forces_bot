import telebot
from telebot import types
import conf
import random
import pandas as pd
import copy
import collections
import psycopg2

bot = telebot.TeleBot(conf.TOKEN)
users = {}
default_settings = {'contest_dict':collections.defaultdict(), 'action':0}
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    users[user_id] = copy.deepcopy(default_settings)
    bot.send_message(user_id, "Привет! Этот бот выдает подборки задач по темам и может сообщить информацию о какой-то конкретной задаче. Чтобы передать команду, используйте /go")

@bot.message_handler(commands=['go'])
def send_welcome(message):
    user_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Информация о задаче", callback_data="button1")
    button2 = types.InlineKeyboardButton(text="Получить контест", callback_data="button2")
    keyboard.add(button1)
    keyboard.add(button2)
    bot.send_message(message.chat.id, "Выберите, что вы хотите от бота", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    if call.message:
        if call.data == "button1":
            users[user_id]['action'] = 1
            bot.send_message(user_id, 'Введите id задачи')
            
        if call.data == "button2":
            users[user_id]['action'] = 2
            bot.send_message(user_id, 'Введите тему и рейтинг в формате рейтинг_тема')

def bot_turn(bot, user_id, query):
    if users[user_id]['action'] == 1:
        conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/code_forces')
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM task_table WHERE id = '%s'""" % query)
        response = cursor.fetchall()
        conn.commit()
        conn.close()
        if len(response) == 0:
            bot.send_message(user_id, 'Такой задачи нет')
        else:
            bot.send_message(user_id, 'Задача номер ' + query +' '+str(response[0][2]) +'\nСсылка: ' + str(response[0][1])+'\nНа темы:'+str(response[0][3])+'\nСложность: ' + str(response[0][4])+'\nЕе решили ' + str(response[0][5]) + ' человек')
    else:
        query = query.lower()
        if query in users[user_id]['contest_dict'].keys():
            num  = users[user_id]['contest_dict'][query] + 1
        else:
            num = 0
        users[user_id]['contest_dict'][query] = num
        query = query+'_'+str(num)
        conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/code_forces')
        cursor = conn.cursor()
        cursor.execute("""SELECT link FROM task_table WHERE group_name = '%s'""" % query)
        response = cursor.fetchall()
        conn.commit()
        conn.close()
        if len(response) == 0:
            bot.send_message(user_id, 'Таких контестов нет')
        else:
            bot.send_message(user_id, 'Ваш контест:' + query)
            contest = ''
            for r in response:
                contest+=r[0]+'\n'
            bot.send_message(user_id, contest)
        

@bot.message_handler(content_types=['text'])
def echo(message):
    user_id = message.chat.id
    query = message.text
    bot_turn(bot, user_id, query)

if __name__ == '__main__':
    bot.polling(none_stop=True)
