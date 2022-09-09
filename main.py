import os
import telebot
import threading
from newUserClass import NewUser
from dotenv import load_dotenv
from telebot import types

from function import *


# Подключаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь новых пользователей чатов писок всех новых пользователей
# и настроек конкретного чата
ConfigDict = {}


# Вывод доступных команд
@bot.message_handler(commands=['help'])
def helps(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    status = confirmation_status_user(message, bot)
    if status:
        bot.send_message(message.chat.id, 'Доступные команды для настройки бота:\n'
                                          '/help — для вызова данного сообщения\n'
                                          '/captcha — меняет тип капчи\n'
                                          '/no_enter_mess — удалять сообщения о входе пользователей в чат\n'
                                          '/enter_mess — отправлять сообщения о входе пользователей в чат\n'
                                          '/attack — активировать проверку новых пользователей\n'
                                          '/no_attack — отключить проверку новых пользователей\n'
                                          '/list_of_links — вывести список доступных ссылок\n'
                                          '/add_links — добавить ссылки в белый список ссылок\n'
                                          '/links — разрешить пользователям отправлять сообщения с ссылками\n'
                                          '/no_links — автоматически удалять сообщения с ссылками\n'
                                          '/start — для запуска бота')


# запуск бота
@bot.message_handler(commands=['start'])
def start(message):
    # Стартовые настройки
    bot.delete_message(message.chat.id, message.message_id)
    status = confirmation_status_user(message, bot)
    if status:
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
# @bot.message_handler(commands=['enter'])
# def enter(message):
#     if message.chat.id not in ConfigDict:
#         return
#
#     bot.delete_message(message.chat.id, message.message_id)
#     if ConfigDict[message.chat.id]['params']['attack']:
#         captcha = ConfigDict[message.chat.id]['params']['captcha']
#         user = NewUser(message, captcha, ConfigDict, bot)
#         ConfigDict[message.chat.id][message.from_user.id] = user
#
#         # Паралельно запускаем таймер у каждого нового пользователя
#         threading.Thread(target=user.timer).start()
#         threading.Thread(target=user.captcha).start()


# Отлавливание нового пользователя
@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    if message.chat.id not in ConfigDict:
        return
    if ConfigDict[message.chat.id]['params']['delEntMess']:
        bot.delete_message(message.chat.id, message.message_id)
    if ConfigDict[message.chat.id]['params']['attack']:
        captcha = ConfigDict[message.chat.id]['params']['captcha']
        user = NewUser(message, captcha, ConfigDict, bot)
        ConfigDict[message.chat.id][message.from_user.id] = user

        # Паралельно запускаем таймер у каждого нового пользователя
        threading.Thread(target=user.timer).start()
        threading.Thread(target=user.captcha).start()


@bot.message_handler(commands=['list_of_links'])
def list_of_links(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.id)
    status = confirmation_status_user(message, bot)
    if status:
        data = return_data_from_json('white_list_links.json')['urls']
        text = "\n".join(url for url in data)
        bot.send_message(message.chat.id, f"Список доступных для отправки ссылок: {text}", disable_web_page_preview=True)


@bot.message_handler(commands=['add_links'])
def add_links(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    status = confirmation_status_user(message, bot)
    if status:
        mess = bot.send_message(message.chat.id, 'Укажите в ответ на это сообщение ссылки,'
                                                 ' которые Вы хотите добавить в список разрешенных ссылок, '
                                                 'разделяя их пробелами')
        ConfigDict[message.chat.id]['mess_links'] = mess


# Удаляет сообщения о входе пользователей
@bot.message_handler(commands=['no_enter_mess'])
def no_enter_message(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    status = confirmation_status_user(message, bot)
    if status:
        ConfigDict[message.chat.id]['params']['delEntMess'] = True


# Разрешает сообщения о входе пользователей
@bot.message_handler(commands=['enter_mess'])
def enter_message(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    status = confirmation_status_user(message, bot)
    if status:
        ConfigDict[message.chat.id]['params']['delEntMess'] = False


# Изменение параметров атаки бота
@bot.message_handler(commands=['attack'])
def attack(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    status = confirmation_status_user(message, bot)
    if status:
        ConfigDict[message.chat.id]['params']['attack'] = True


@bot.message_handler(commands=['no_attack'])
def no_attack(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    user_status = confirmation_status_user(message, bot)
    if user_status:
        ConfigDict[message.chat.id]['params']['attack'] = False


# Изменение параметров удаления ссылок
@bot.message_handler(commands=['links'])
def links(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    user_status = confirmation_status_user(message, bot)
    if user_status:
        ConfigDict[message.chat.id]['params']['links'] = False


@bot.message_handler(commands=['no_links'])
def no_links(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.message_id)
    user_status = confirmation_status_user(message, bot)
    if user_status:
        ConfigDict[message.chat.id]['params']['links'] = True


# Вывод всех новых пользователей
# @bot.message_handler(commands=['getUsers'])
# def get_users(message):
#     bot.send_message(message.chat.id, f'{ConfigDict}')


# Смена настроек капчи
@bot.message_handler(commands=['captcha'])
def set_captcha(message):
    if message.chat.id not in ConfigDict:
        return
    bot.delete_message(message.chat.id, message.id)
    user_status = confirmation_status_user(message, bot)
    if user_status:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('Кнопка', callback_data='set-cpt button')
        button2 = types.InlineKeyboardButton('Арифметический пример', callback_data='set-cpt math')
        button3 = types.InlineKeyboardButton('Изображение с цифрами', callback_data='set-cpt pic')
        markup.add(button1, button2, button3)

        bot.send_message(message.chat.id, 'Выберите тип капчи', reply_markup=markup)


# Отлавливание капчу с кнопкой и смену настроек капчи
@bot.callback_query_handler(func=lambda call: True)
def chek_captcha(call):
    if call.message.chat.id not in ConfigDict:
        return

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
        threading.Thread(target=delete_message_timer(mess, bot)).start()
        ConfigDict[chat_id].pop(user_id)
        return

    user_info = bot.get_chat_member(call.message.chat.id, call.from_user.id)
    user_status = user_info.status
    if user_status in ['creator', 'administrator']:
        if call_words[0] == 'set-cpt':
            ConfigDict[chat_id]['params']['captcha'] = call_words[1]

            mes = bot.send_message(chat_id, 'Тип капчи изменен')
            bot.delete_message(chat_id, call.message.message_id)
            bot.delete_message(chat_id, mes.id)


# Запрет на отправку сообщений пользователям,
# непрошедшим капчу (которые находятся в словаре)
@bot.message_handler(func=lambda call: True)
def check_message(message):
    if message.chat.id not in ConfigDict:
        return

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
            ConfigDict[chat_id].pop(user_id)
            threading.Thread(target=delete_message_timer(mess, bot)).start()
            return

        else:
            mess = bot.send_message(chat_id, f'{first_name} {last_name} Вы где-то ошиблись. Попробуйте снова')
            bot.delete_message(chat_id, message.message_id)
            threading.Thread(target=delete_message_timer(mess, bot)).start()
            return

    # Удаление сообщений пользователей, непрошедший проверку
    elif user_id in ConfigDict[chat_id]:
        bot.delete_message(chat_id, message_id)
        return

    user_status = confirmation_status_user(message, bot)

    # Проверяем, есть ли ссылки в списке доступных ссылок
    short_urls = return_short_urls(message)
    data = return_data_from_json('white_list_links.json')
    links_conform = find_allowed_urls(short_urls, data)

    # Удаление ссылок пользователей
    if ConfigDict[message.chat.id]['params']['links'] and not links_conform and not user_status:
        if message.entities is not None:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    bot.delete_message(message.chat.id, message.message_id)
                    return

    # Добавляем ссылки в белый список
    if message.reply_to_message and user_status and 'mess_links' in ConfigDict[chat_id]:
        if message.reply_to_message.id == ConfigDict[chat_id]['mess_links'].id:
            if message.entities is not None:
                write_data_in_json(data, short_urls, 'white_list_links.json')
        bot.delete_message(message.chat.id, message.reply_to_message.id)
        bot.delete_message(message.chat.id, message.id)


bot.infinity_polling()
