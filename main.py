import os
import telebot
import threading
import json
from pprint import pprint
from newUserClass import NewUser
from dotenv import load_dotenv


# Подключаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь новых пользователей чатов писок всех новых пользователей
newUserDict = {}


# Вывод доступных команд
@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id, 'Доступные команды для настройки бота:\n'
                                      '/help - для вызова данного сообщения\n'
                                      '/captcha — меняет тип капчи\n'
                                      '/deleteEntryMessages — удалять сообщения о входе пользователей в чат\n'
                                      '/greeting — встречать прошедших проверку пользователей сообщением\n'
                                      '/noAttack — отключить SpamBOT\n'
                                      '/noLinks — автоматически удалять сообщения со ссылками\n'
                                      '/enter - эмитация входа пользователя\n'
                                      '/getUsers - возвращает список новых пользователей\n'
                                      '/start - для запуска бота')


# запуск бота
@bot.message_handler(commands=['start'])
def start(message):
    newUserDict[message.chat.id] = {}


# Отлавливание входа нового пользователя
@bot.message_handler(commands=['enter'])
def enter(message):
    user = NewUser(message, 'button',newUserDict, bot)
    newUserDict[message.chat.id][message.from_user.id] = user

    # Паралельно запускаем таймер у каждого нового пользователя
    threading.Thread(target=user.timer).start()
    user.button_captcha()


# Вывод всех новых пользователей
@bot.message_handler(commands=['getUsers'])
def get_users(message):
    bot.send_message(message.chat.id, f'{newUserDict}')


# Отлавливание капчи
@bot.callback_query_handler(func=lambda call: True)
def chek_captcha(call):
    call_words = call.data.split()
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call_words[0] == 'cpt' and call_words[1] == str(user_id):

        newUserDict[chat_id][user_id].captcha_is_done()

        bot.send_message(chat_id, f" Вы успешно прошли капчу, @{call.from_user.username}!"
                                  f" Добро пожаловать в чат дольщиков.")

        del newUserDict[chat_id][user_id]


# Запрет на отправку сообщений пользователям,
# непрошедшим капчу (которые находятся в словаре)
@bot.message_handler(func=lambda call: True)
def delete_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id

    if user_id in newUserDict[chat_id]:
        bot.delete_message(chat_id, message_id)




bot.infinity_polling()
