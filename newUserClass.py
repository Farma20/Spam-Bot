from accessify import private


class NewUser(object):
    def __init__(self, id):
        self.__userID = id
        self.__time = 60

    def get_user_id(self):
        return self.__userID

    @staticmethod
    def timer(self):
        print('Coming soon')
        pass
