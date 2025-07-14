import os


class Notification:
    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message

    def notify(self):
        os.system(f'notify-send "{self.title}" "{self.message}"')
