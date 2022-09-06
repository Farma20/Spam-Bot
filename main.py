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
    newUserList[message.chat.id] = {}


@bot.message_handler(commands=['enter'])
def enter(message):
    user = NewUser(message, 'button', bot)
    newUserList[message.chat.id][message.from_user.id] = user

    # Паралельно запускаем таймер у каждого нового пользователя
    threading.Thread(target=user.timer).start()
    user.button_captcha()


@bot.message_handler(commands=['getUsers'])
def get_users(message):
    bot.send_message(message.chat.id, f'{newUserList}')


@bot.callback_query_handler(func=lambda call: True)
def chek_captcha(call):
    call_words = call.data.split()
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call_words[0] == 'cpt' and call_words[1] == str(user_id):

        newUserList[chat_id][user_id].captcha_is_done()

        bot.send_message(chat_id, f" Вы успешно прошли капчу, @{call.from_user.username}!"
                                  f" Добро пожаловать в чат дольщиков.")

        del newUserList[chat_id][user_id]




bot.infinity_polling()
