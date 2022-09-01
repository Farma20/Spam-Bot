import time
from telebot import types


class NewUser(object):
    def __init__(self, user_name, user_id, chat_id, type_captcha, bot):
        self.__userName = user_name
        self.__userID = user_id
        self.__chatID = chat_id
        self.__type = type_captcha
        self.__time = 5
        self.__captcha_is_done = False
        self.__is_kick = False
        self.bot = bot

    def get_user_name(self):
        return self.__userName

    def get_user_id(self):
        return self.__userID

    def get_chat_id(self):
        return self.__chatID

    def button_captcha(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Я не бот', callback_data=f'cpt {self.__userID}'))
        self.bot.send_message(self.__chatID, f'Здравствуйте {self.__userName}, чтобы отправлять сообщения в чат Вам'
                                             f'необходимо доказать, что вы не робот, нажав на кнопку снизу.'
                                             f' В ином случае Вас автоматически удалят из чата'
                                             f' через {self.__time} секунд', reply_markup=markup)

    def timer(self):
        timing_start = time.time()
        self.button_captcha()

        while True:
            if self.__captcha_is_done:
                self.bot.send_message(self.__chatID, f'Добро пожаловать в чат дольщиков!')
                break

            if time.time() - timing_start >= self.__time:
                self.bot.send_message(self.__chatID, f'Пользователь кикнут')
                break

