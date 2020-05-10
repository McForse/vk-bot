import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from schedule import Schedule
from database import Database
from handler import Handler

from config import log, vk_api_token as token


class Bot:

    def __init__(self):
        self.__schedule = Schedule()

        self.__vk_session = vk_api.VkApi(token=token)
        self.__vk = self.__vk_session.get_api()

        self.__longpoll = VkLongPoll(self.__vk_session)
        self.__database = Database()
        self.__handler = Handler(self.__database, self.__schedule)

    def start(self):
        print("Bot started...")

        for event in self.__longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.text and event.to_me:
                uid = event.user_id
                text = event.text

                if log:
                    print('New message from {}, text = {}'.format(uid, text))

                # Обработка запроса
                res = self.__handler.handle(uid, text.lower())

                # Сообщение
                if res.get_keyboard() is None:
                    self.send_message(uid, res.get_message())

                # Клавиатура
                elif res.get_keyboard() is not None:
                    self.send_keyboard(uid, res.get_message(), res.get_keyboard())

    def send_message(self, user_id, message):
        self.__vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message)

    def send_keyboard(self, user_id, message, keyboard):
        self.__vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message=message)
