import os
import telebot
from newUserClass import NewUser
from dotenv import load_dotenv


#Подключаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id, 'Доступные команды для настройки бота:\n'
                                      '/help - для вызова данного сообщения\n'
                                      '/captcha — меняет тип капчи\n'
                                      '/deleteEntryMessages — удалять сообщения о входе пользователей в чат\n'
                                      '/greeting — встречать прошедших проверку пользователей сообщением\n'
                                      '/noAttack — отключить SpamBOT\n'
                                      '/noLinks — автоматически удалять сообщения со ссылками\n')


@bot.message_handler(commands=['start'])
def start(message):
    user = NewUser(message.from_user.id)
    bot.send_message(message.chat.id, user.get_user_id())
    bot.send_message(message.chat.id, message.chat.id)


bot.infinity_polling()
