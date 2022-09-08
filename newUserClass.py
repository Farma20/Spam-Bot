import time
import random
import string
from telebot import types
from captcha.image import ImageCaptcha


class NewUser(object):
    def __init__(self, message, type_captcha, user_dict, bot):
        self.__userName = message.from_user.username
        self.__userID = message.from_user.id
        self.__chatID = message.chat.id
        self.__type_captcha = type_captcha
        self.__time = 60
        self.__captcha_is_done = False
        self.__is_kick = False
        self.__catha_answer = ''
        self.user_dict = user_dict
        self.bot = bot

    # геттеры
    def get_user_name(self):
        return self.__userName

    def get_user_id(self):
        return self.__userID

    def get_chat_id(self):
        return self.__chatID

    def get_captcha_answer(self):
        return self.__catha_answer

    # Функция смены значения прохождения капчи
    def captcha_is_done(self):
        self.__captcha_is_done = True

    # Функция создания капчи-кнопки
    def captcha(self):
        if self.__type_captcha == 'button':
            self.button_captcha()

        elif self.__type_captcha == 'math':
            self.math_captcha()

        elif self.__type_captcha == 'pic':
            self.pic_captcha()

    def button_captcha(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Я не бот', callback_data=f'cpt {self.__userID}'))
        self.bot.send_message(self.__chatID, f'Здравствуйте @{self.__userName}, чтобы отправлять сообщения в чат Вам '
                                             f'необходимо доказать, что вы не робот, нажав на кнопку снизу.'
                                             f' В ином случае Вас автоматически удалят из чата'
                                             f' через {self.__time} секунд', reply_markup=markup)

    def math_captcha(self):
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        self.__catha_answer = str(num1 + num2)
        self.bot.send_message(self.__chatID, f'Здравствуйте @{self.__userName}, чтобы отправлять сообщения в чат Вам '
                                             f'необходимо доказать, что вы не робот, отправив в ответ на данное'
                                             f' сообщение решение следующего арифметического выражения:\n'
                                             f'{num1} + {num2} = ? \n'
                                             f' В ином случае Вас автоматически удалят из чата'
                                             f' через {self.__time} секунд')

    def pic_captcha(self):
        image = ImageCaptcha(width=280, height=90)
        captcha_pic = ''.join(random.choice(string.digits) for i in range(6))
        self.__catha_answer = captcha_pic
        data = image.generate(captcha_pic)
        self.bot.send_photo(self.__chatID, data, f'Здравствуйте @{self.__userName}, чтобы отправлять сообщения в чат Вам '
                                             f'необходимо доказать, что вы не робот, отправив в ответ на данное'
                                             f' сообщение текст, изображенный на картинке'
                                             f' В ином случае Вас автоматически удалят из чата'
                                             f' через {self.__time} секунд')

    # Таймер
    def timer(self):
        timing_start = time.time()

        while True:
            if self.__captcha_is_done:
                break

            if time.time() - timing_start >= self.__time:
                self.bot.kick_chat_member(self.__chatID, self.__userID)
                break

