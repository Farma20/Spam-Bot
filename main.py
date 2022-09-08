import os
import re
import time
import telebot
import threading
import json
from newUserClass import NewUser
from dotenv import load_dotenv
from telebot import types


# Подключаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь новых пользователей чатов писок всех новых пользователей
# и настроек конкретного чата
ConfigDict = {}


# таймер для удаления сообщений
def delete_message_timer(message):
    timing_start = time.time()

    while True:
        if time.time() - timing_start >= 5:
            bot.delete_message(message.chat.id, message.message_id)
            break


# Вывод доступных команд
@bot.message_handler(commands=['help'])
def helps(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        bot.send_message(message.chat.id, 'Доступные команды для настройки бота:\n'
                                          '/help — для вызова данного сообщения\n'
                                          '/captcha — меняет тип капчи\n'
                                          '/no_enter_mess — удалять сообщения о входе пользователей в чат\n'
                                          '/enter_mess — отправлять сообщения о входе пользователей в чат\n'
                                          '/attack — активировать проверку новых пользователей\n'
                                          '/no_attack — отключить проверку новых пользователей\n'
                                          '/add_links — добавить ссылки в белый список ссылок\n'
                                          '/links — разрешить пользователям отправлять сообщения с ссылками\n'
                                          '/no_links — автоматически удалять сообщения с ссылками\n'
                                          '/start — для запуска бота')


# запуск бота
@bot.message_handler(commands=['start'])
def start(message):
    # Стартовые настройки
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id] = {
            'params': {'delEntMess': True,
                       'captcha': 'math',
                       'attack': True,
                       'links': True}
        }

        bot.send_message(message.chat.id, 'Здравствуйте, данный бот-антиспам предназначен для предотвращения '
                                          'присоединения в чат спам ботов. Чтобы посмотреть все возможные '
                                          'команды этого бота введите команду /help')


# Отлавливание входа нового пользователя
@bot.message_handler(commands=['enter'])
def enter(message):
    if ConfigDict[message.chat.id]['params']['attack']:
        captcha = ConfigDict[message.chat.id]['params']['captcha']
        user = NewUser(message, captcha, ConfigDict, bot)
        ConfigDict[message.chat.id][message.from_user.id] = user

        # Паралельно запускаем таймер у каждого нового пользователя
        threading.Thread(target=user.timer).start()
        threading.Thread(target=user.captcha).start()



# Отлавливание нового пользователя
@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    if ConfigDict[message.chat.id]['params']['delEntMess']:
        bot.delete_message(message.chat.id, message.message_id)
    if ConfigDict[message.chat.id]['params']['attack']:
        captcha = ConfigDict[message.chat.id]['params']['captcha']
        user = NewUser(message, captcha, ConfigDict, bot)
        ConfigDict[message.chat.id][message.from_user.id] = user

        # Паралельно запускаем таймер у каждого нового пользователя
        threading.Thread(target=user.timer).start()
        threading.Thread(target=user.captcha).start()


@bot.message_handler(commands=['add_links'])
def add_links(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        mess = bot.send_message(message.chat.id, 'Укажите в ответ на это ссылки,'
                                                 ' которые Вы хотите добавить в белый список, '
                                                 'разделяя их пробелами')
        ConfigDict[message.chat.id]['mess_links'] = mess
        bot.delete_message(message.chat.id, message.id)


# Удаляет сообщения о входе пользователей
@bot.message_handler(commands=['no_enter_mess'])
def no_enter_message(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id]['params']['delEntMess'] = True
        bot.delete_message(message.chat.id, message.id)


# Разрешает сообщения о входе пользователей
@bot.message_handler(commands=['enter_mess'])
def enter_message(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id]['params']['delEntMess'] = False
        bot.delete_message(message.chat.id, message.id)


# Изменение параметров атаки бота
@bot.message_handler(commands=['attack'])
def attack(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id]['params']['attack'] = True
        bot.delete_message(message.chat.id, message.id)


@bot.message_handler(commands=['no_attack'])
def no_attack(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id]['params']['attack'] = False
        bot.delete_message(message.chat.id, message.id)


# Изменение параметров удаления ссылок
@bot.message_handler(commands=['links'])
def links(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id]['params']['links'] = True
        bot.delete_message(message.chat.id, message.id)


@bot.message_handler(commands=['no_links'])
def no_links(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        ConfigDict[message.chat.id]['params']['links'] = False
        bot.delete_message(message.chat.id, message.id)


# Вывод всех новых пользователей
@bot.message_handler(commands=['getUsers'])
def get_users(message):
    bot.send_message(message.chat.id, f'{ConfigDict}')


# Смена настроек капчи
@bot.message_handler(commands=['captcha'])
def set_captcha(message):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    bot.delete_message(message.chat.id, message.id)
    if status in ['creator', 'administrator']:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('Кнопка', callback_data='set-cpt button')
        button2 = types.InlineKeyboardButton('Арифметический пример', callback_data='set-cpt math')
        button3 = types.InlineKeyboardButton('Изображение с цифрами', callback_data='set-cpt pic')
        markup.add(button1, button2, button3)

        bot.send_message(message.chat.id, 'Выберите тип капчи', reply_markup=markup)


# Отлавливание капчу с кнопкой и смену настроек капчи
@bot.callback_query_handler(func=lambda call: True)
def chek_captcha(call):
    call_words = call.data.split()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    first_name = call.from_user.first_name
    last_name = call.from_user.last_name

    if call_words[0] == 'cpt' and call_words[1] == str(user_id):

        ConfigDict[chat_id][user_id].captcha_is_done()

        mess = bot.send_message(chat_id, f" Вы успешно прошли капчу, {first_name} {last_name}!"
                                         f" Добро пожаловать в чат дольщиков.")

        bot.delete_message(chat_id, call.message.message_id)
        threading.Thread(target=delete_message_timer(mess)).start()
        del ConfigDict[chat_id][user_id]

    user_info = bot.get_chat_member(call.message.chat.id, call.from_user.id)
    status = user_info.status
    if status in ['creator', 'administrator']:
        if call_words[0] == 'set-cpt':
            ConfigDict[chat_id]['params']['captcha'] = call_words[1]

            mes = bot.send_message(chat_id, 'Тип капчи изменен')
            bot.delete_message(chat_id, call.message.message_id)
            bot.delete_message(chat_id, mes.id)

# Запрет на отправку сообщений пользователям,
# непрошедшим капчу (которые находятся в словаре)
@bot.message_handler(func=lambda call: True)
def check_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Проверка верности капчи (арифметика\текст)
    # при ответе на сообщение бота
    if user_id in ConfigDict[chat_id]:
        if ConfigDict[chat_id][user_id].get_captcha_answer() == message.text:
            ConfigDict[chat_id][user_id].captcha_is_done()

            mess = bot.send_message(chat_id, f" Вы успешно прошли капчу, {first_name} {last_name}!"
                                             f" Добро пожаловать в чат дольщиков.")
            captcha_mess = ConfigDict[chat_id][user_id].get_captcha_mess()
            bot.delete_message(chat_id, captcha_mess.id)
            bot.delete_message(chat_id, message.message_id)
            threading.Thread(target=delete_message_timer(mess)).start()
            del ConfigDict[chat_id][user_id]

        else:
            mess = bot.send_message(chat_id, f'{first_name} {last_name} Вы где-то ошиблись. Попробуйте снова')
            bot.delete_message(chat_id, message.message_id)
            threading.Thread(target=delete_message_timer(mess)).start()

    # Удаление сообщений пользователей, непрошедший проверку
    elif user_id in ConfigDict[chat_id]:
        bot.delete_message(chat_id, message_id)

    # Удаление ссылок пользователей
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    if ConfigDict[message.chat.id]['params']['links'] and status not in ['creator', 'administrator']:
        if message.entities is not None:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    bot.delete_message(message.chat.id, message.message_id)
    
    # Добавляем ссылки в белый список
    if message.reply_to_message.id == ConfigDict[chat_id]['mess_links'].id and status in ['creator', 'administrator']:
        if message.entities is not None:
            links_from_message = re.findall(r'(https?://[^\s]+)', message.text)

            try:
                with open('white_list_links.json', 'r') as file:
                    data = json.load(file)
            except:
                data = ''

            if len(data) == 0:
                data = {'urls': links_from_message}
            else:
                data['urls'].append(links_from_message)

            with open('white_list_links.json', 'w') as file:
                json.dump(data, file)






bot.infinity_polling()
