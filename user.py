class User:

    def __init__(self, group):
        self.__group = group
        self.__temp_group = None

    def get_group(self):
        return self.__group

    def set_group(self, group):
        self.__group = group

    def get_temp_group(self):
        return self.__temp_group

    def set_temp_group(self, temp_group):
        self.__temp_group = temp_group

    def remove_temp(self):
        self.__temp_group = None
