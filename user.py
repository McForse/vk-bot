class User:

    def __init__(self, group):
        self.__group = group
        self.__temp_group = None
        self.__weather_city = 'Москва'

    def get_group(self):
        return self.__group

    def set_group(self, group):
        self.__group = group

    def get_temp(self):
        return self.__temp_group

    def set_temp(self, temp_group):
        self.__temp_group = temp_group

    def remove_temp(self):
        self.__temp_group = None

    def get_weather_city(self):
        return self.__weather_city

    def set_weather_city(self, city):
        self.__weather_city = city
