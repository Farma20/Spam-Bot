import os
import telebot
import threading
from newUserClass import NewUser
from dotenv import load_dotenv


# Подключаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь новых пользователей чатов писок всех новых пользователей
newUserList = {}




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


@bot.message_handler(commands=['start'])
def start(message):
    newUserList[message.chat.id] = []



@bot.message_handler(commands=['enter'])
def enter(message):
    bot.send_message(message.chat.id, f'Здравствуй {message.from_user.username}!'
                                      f' Чтобы оставаться в чате и отправлять сообщения'
                                      f' тебе необходимо пройти проверку на робота')
    user = NewUser(message.from_user.id, message.chat.id)
    newUserList[message.chat.id].append(user)

    # Паралельно запускаем таймер у каждого нового пользователя
    threading.Thread(target=user.timer).start()



@bot.message_handler(commands=['getUsers'])
def get_users(message):
    bot.send_message(message.chat.id, f'{newUserList}')


bot.infinity_polling()
