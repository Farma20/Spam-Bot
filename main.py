import os
import telebot
import threading
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


# Вывод доступных команд
@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id, 'Доступные команды для настройки бота:\n'
                                      '/help - для вызова данного сообщения\n'
                                      '/captcha — меняет тип капчи\n'
                                      '/deleteEntryMessages — удалять сообщения о входе пользователей в чат\n'
                                      '/attack — отключить SpamBOT\n'
                                      '/noLinks — автоматически удалять сообщения со ссылками\n'
                                      '/enter - эмитация входа пользователя\n'
                                      '/getUsers - возвращает список новых пользователей\n'
                                      '/start - для запуска бота')


# запуск бота
@bot.message_handler(commands=['start'])
def start(message):
    # Стартовые настройки
    ConfigDict[message.chat.id] = {
                                    'params': {'delEntMess': True,
                                               'captcha': 'text',
                                               'attack': True,
                                               'links': True}
    }


# Отлавливание входа нового пользователя
@bot.message_handler(commands=['enter'])
def enter(message):
    if ConfigDict[message.chat.id]['params']['attack']:
        captcha = ConfigDict[message.chat.id]['params']['captcha']
        user = NewUser(message, captcha, ConfigDict, bot)
        ConfigDict[message.chat.id][message.from_user.id] = user

        # Паралельно запускаем таймер у каждого нового пользователя
        threading.Thread(target=user.timer).start()
        user.captcha()


# Удаляет сообщения о входе пользователей
@bot.message_handler(comamds=['deleteEntryMessages'])
def delete_entry_messages(message):
    if ConfigDict[message.chat.id]['params']['delEntMess']:
        ConfigDict[message.chat.id]['params']['delEntMess'] = False

        bot.send_message(message.chat.id, 'Удаление сообщений о входе новых пользователей ОТКЛЮЧЕНО')
    else:
        ConfigDict[message.chat.id]['params']['delEntMess'] = True

        bot.send_message(message.chat.id, 'Удаление сообщений о входе новых пользователей ВКЛЮЧЕНО')


# Изменение параметров атаки бота
@bot.message_handler(commands=['attack'])
def attack(message):
    if ConfigDict[message.chat.id]['params']['attack']:
        ConfigDict[message.chat.id]['params']['attack'] = False

        bot.send_message(message.chat.id, 'Проверка новых пользователей ОТКЛЮЧЕНА')
    else:
        ConfigDict[message.chat.id]['params']['attack'] = True

        bot.send_message(message.chat.id, 'Проверка новых пользователей ВКЛЮЧЕНА')


# Изменение параметров удаления ссылок
@bot.message_handler(commands=['links'])
def links(message):
    if ConfigDict[message.chat.id]['params']['links']:
        ConfigDict[message.chat.id]['params']['links'] = False

        bot.send_message(message.chat.id, 'Удаление ссылок пользователей ОТКЛЮЧЕНА')
    else:
        ConfigDict[message.chat.id]['params']['links'] = True

        bot.send_message(message.chat.id, 'Удаление ссылок пользователей ВКЛЮЧЕНА')


# Вывод всех новых пользователей
@bot.message_handler(commands=['getUsers'])
def get_users(message):
    bot.send_message(message.chat.id, f'{ConfigDict}')


# Смена настроек капчи
@bot.message_handler(commands=['captcha'])
def set_captcha(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Кнопка', callback_data='set-cpt button')
    button2 = types.InlineKeyboardButton('Арифметический пример', callback_data='set-cpt math')
    button3 = types.InlineKeyboardButton('Текст с изображения', callback_data='set-cpt text')
    markup.add(button1, button2, button3)

    bot.send_message(message.chat.id, 'Выберите тип капчи', reply_markup=markup)


# Отлавливание капчи и смены ее настроек
@bot.callback_query_handler(func=lambda call: True)
def chek_captcha(call):
    call_words = call.data.split()
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call_words[0] == 'cpt' and call_words[1] == str(user_id):

        ConfigDict[chat_id][user_id].captcha_is_done()

        bot.send_message(chat_id, f" Вы успешно прошли капчу, @{call.from_user.username}!"
                                  f" Добро пожаловать в чат дольщиков.")

        del ConfigDict[chat_id][user_id]

    if call_words[0] == 'set-cpt':
        ConfigDict[chat_id]['params']['captcha'] = call_words[1]

        bot.send_message(chat_id, 'Тип капчи изменен')


# Запрет на отправку сообщений пользователям,
# непрошедшим капчу (которые находятся в словаре)
@bot.message_handler(func=lambda call: True)
def delete_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id

    # Проверка верности капчи (арифметика тест)
    # при ответе на сообщение бота
    if message.reply_to_message and user_id in ConfigDict[chat_id]:
        if ConfigDict[chat_id][user_id].get_captcha_answer() == message.text:
            ConfigDict[chat_id][user_id].captcha_is_done()

            bot.send_message(chat_id, f" Вы успешно прошли капчу, @{message.from_user.username}!"
                                      f" Добро пожаловать в чат дольщиков.")

            del ConfigDict[chat_id][user_id]

        else:
            bot.reply_to(message, 'Не верно. Попробуйте снова')


    # Удаление сообщений пользователей, непрошедший проверку
    elif user_id in ConfigDict[chat_id]:
        bot.delete_message(chat_id, message_id)

    # Удаление ссылок пользователей
    if ConfigDict[message.chat.id]['params']['links']:
        if message.entities is not None:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    bot.delete_message(message.chat.id, message.message_id)


bot.infinity_polling()
