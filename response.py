class Response:

    def __init__(self, message='', keyboard=None, image=None):
        self.message = message
        self.keyboard = keyboard
        self.image = image

    def get_message(self):
        return self.message

    def get_keyboard(self):
        return self.keyboard

    def get_image(self):
        return self.image
