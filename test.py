from schedule import Schedule
import re
from datetime import datetime, timedelta

class UIO:
    def __init__(self, a):
        self.__a = a

    def set_a(self, a):
        self.__a = a

    def str(self):
        return self.__a
l = {1:1}
print(1 in l)