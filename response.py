class Response:

    def __init__(self, message='', keyboard=None):
        self.__message = message
        self.__keyboard = keyboard

    def get_message(self):
        return self.__message

    def get_keyboard(self):
        return self.__keyboard
