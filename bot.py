import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from schedule import Schedule
from database import Database
from handler import Handler

from config import log, vk_api_token as token


class Bot:

    def __init__(self):
        self.__schedule = Schedule()

        self.__vk = vk_api.VkApi(token=token)
        self.__vk_api = self.__vk.get_api()

        self.__longpoll = VkLongPoll(self.__vk)
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
                res = self.__handler.handle(uid, text)

                # Сообщение
                if res.is_message():
                    self.send_message(uid, res.get_message())

                # Клавиатура
                elif res.get_keyboard() is not None:
                    self.send_keyboard(uid, res.get_message(), res.get_keyboard())

                # Картинка с заголовком
                elif res.get_image() is not None and res.get_title() is not None:
                    self.send_title_image(uid, res.get_title(), res.get_message(), res.get_image())

                # Картинка
                elif res.get_image() is not None:
                    self.send_image(uid, res.get_message(), res.get_image())

    def send_message(self, user_id, message):
        self.__vk_api.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message)

    def send_keyboard(self, user_id, message, keyboard):
        self.__vk_api.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message=message)

    def send_image(self, user_id, message, image):
        attachments = self.upload_image(image)

        self.__vk_api.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            attachment=','.join(attachments),
            message=message)

    def send_title_image(self, user_id, title, message, image):
        self.send_message(user_id, title)
        self.send_image(user_id, '', image)
        self.send_message(user_id, message)

    def upload_image(self, image):
        server = self.__vk.method("photos.getMessagesUploadServer")
        post_req = requests.post(server["upload_url"], files={"photo": open(image, "rb")}).json()

        save = self.__vk.method("photos.saveMessagesPhoto", {"photo": post_req["photo"],
                                                             "server": post_req["server"],
                                                             "hash": post_req["hash"]})[0]
        attachments = ["photo{}_{}".format(save["owner_id"], save["id"])]
        return attachments
