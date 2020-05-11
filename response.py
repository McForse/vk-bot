class Response:

    def __init__(self, message='', keyboard=None, image=None, title=None):
        self.message = message
        self.keyboard = keyboard
        self.image = image
        self.title = title

    def get_message(self):
        return self.message

    def get_keyboard(self):
        return self.keyboard

    def get_image(self):
        return self.image

    def get_title(self):
        return self.title

    def is_message(self):
        return self.keyboard is None and self.image is None
