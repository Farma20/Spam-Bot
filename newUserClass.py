import time
from telebot import types


class NewUser(object):
    def __init__(self, message, type_captcha, bot):
        self.__userName = message.from_user.username
        self.__userID = message.from_user.id
        self.__chatID = message.chat.id
        self.__type = type_captcha
        self.__time = 10
        self.__captcha_is_done = False
        self.__is_kick = False
        self.bot = bot

    def get_user_name(self):
        return self.__userName

    def get_user_id(self):
        return self.__userID

    def get_chat_id(self):
        return self.__chatID

    def captcha_is_done(self):
        self.__captcha_is_done = True

    def button_captcha(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Я не бот', callback_data=f'cpt {self.__userID}'))
        self.bot.send_message(self.__chatID, f'Здравствуйте @{self.__userName}, чтобы отправлять сообщения в чат Вам '
                                             f'необходимо доказать, что вы не робот, нажав на кнопку снизу.'
                                             f' В ином случае Вас автоматически удалят из чата'
                                             f' через {self.__time} секунд', reply_markup=markup)

    def timer(self):
        timing_start = time.time()

        while True:
            if self.__captcha_is_done:
                self.bot.send_message(self.__chatID, 'Таймер отключен')
                break

            if time.time() - timing_start >= self.__time:
                self.bot.send_message(self.__chatID, f'Пользователь кикнут')
                break

    def __del__(self):
        self.bot.send_message(self.__chatID, f'Удален')

