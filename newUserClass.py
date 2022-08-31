import time


class NewUser(object):
    def __init__(self, user_id, chat_id):
        self.__userID = user_id
        self.__chatID = chat_id
        self.__time = 60
        self.__captcha_is_done = False
        self.__is_kick = False

    def get_user_id(self):
        return self.__userID

    def get_chat_id(self):
        return self.__chatID

    def timer(self):
        print('Таймер запущен')

        timing_start = time.time()

        while True:
            if self.__captcha_is_done:
                print('Капча пройдена')
                break

            if time.time() - timing_start >= self.__time:
                print('Пользователь кикнут')
                break

