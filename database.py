from user import User


class Database:

    def __init__(self):
        self.__users = {}
        self.set_user_group(105205179, 'ИКБО-08-19')

    def get_user_group(self, uid):
        return self.__users.get(uid).get_group()

    def set_user_group(self, uid, group):
        if uid in self.__users:
            self.__users.get(uid).set_group(group)
        else:
            self.__users[uid] = User(group)

    def get_user_temp(self, uid):
        return self.__users.get(uid)

    def set_user_temp(self, uid, temp_group):
        if uid in self.__users:
            self.__users.get(uid).set_temp(temp_group)

    def remove_user_temp(self, uid):
        if uid in self.__users:
            self.__users.get(uid).remove_temp()

    def get_user_last_group(self, uid):
        if uid in self.__users:
            if self.__users.get(uid).get_temp():
                return self.__users.get(uid).get_temp()
            else:
                return self.__users.get(uid).get_group()

    def get_weather_city(self, uid):
        if uid in self.__users:
            return self.__users.get(uid).get_weather_city()

    def set_weather_city(self, uid, city):
        if uid in self.__users:
            return self.__users.get(uid).set_weather_city(city)

    def user_exist(self, uid):
        return uid in self.__users
