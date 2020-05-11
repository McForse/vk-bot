import re
from response import Response
from coronavirus import Coronavirus
from datetime import datetime
from weather import Weather
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import config

REGEX_COMMAND = '^{} .*'


class Handler:

    def __init__(self, database, schedule):
        self.__database = database
        self.__schedule = schedule
        self.__coronavirus = Coronavirus()

    def handle(self, user_id, text):

        # Установка группы
        if re.search(config.REGEX_GROUP, text.upper()):
            group = text.upper()

            if self.__schedule.group_exist(group):
                self.__database.set_user_group(user_id, text.upper())
                return Response('Я запомнил, что ты из группы ' + group)
            else:
                return Response('Такой группы нет')

        # Номер группы
        elif text == 'какая группа?':
            if self.__database.user_exist(user_id):
                return Response('Показываю расписание группы {}'.format(self.__database.get_user_group(user_id)))
            else:
                return Response('Я не знаю в какой вы группе')

        # Номер недели
        elif text == 'какая неделя?':
            return Response('Идёт {} неделя'.format(self.__schedule.get_study_week_number()))

        # Меню с расписанием с дополнительными параметрами
        elif re.search(REGEX_COMMAND.format('бот'), text):
            commands = text.split()

            # Расписание на определённый день недели
            if commands[1] in config.week_days_interpreter:

                # Для конкретной группы
                if len(commands) == 3:
                    group = commands[2].upper()

                    if re.search(config.REGEX_GROUP, group):
                        if self.__schedule.group_exist(group):
                            message = self.__schedule.get_day_schedule(group=group,
                                                                       week_day=config.week_days_interpreter[
                                                                           commands[1]])
                            return Response(message)
                        else:
                            return Response('Такой группы нет')
                    else:
                        return Response('Неизвестная команда')

                # Для группы пользователя
                elif len(commands) == 2:
                    if self.__database.user_exist(user_id):
                        message = self.__schedule.get_day_schedule(group=self.__database.get_user_last_group(user_id),
                                                                   week_day=config.week_days_interpreter[commands[1]])
                        return Response(message)
                    else:
                        return Response('Я не знаю в какой вы группе')
                else:
                    return Response('Неизвестная команда')

            # Меню с расписанием для конкретной группы
            elif re.search(config.REGEX_GROUP, commands[1].upper()):
                group = commands[1].upper()

                if self.__schedule.group_exist(group):
                    self.__database.set_user_temp_group(user_id, group)
                    return self.get_keyboard_schedule('Показать расписание группы {} ...'.format(group))
                else:
                    return Response('Такой группы нет')
            else:
                return Response('Неизвестная команда')

        # Меню с расписанием
        elif text == 'бот' or text == 'Показать расписание':
            self.__database.remove_user_temp(user_id)
            return self.get_keyboard_schedule('Показать расписание ...')

        # Расписание на сегодня
        elif text == 'на сегодня':
            if self.__database.user_exist(user_id):
                message = self.__schedule.get_day_schedule(self.__database.get_user_last_group(user_id))
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Расписание на завтра
        elif text == 'на завтра':
            if self.__database.user_exist(user_id):
                message = self.__schedule.get_day_schedule(self.__database.get_user_last_group(user_id), 1)
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Расписание на эту неделю
        elif text == 'на неделю' or text == 'на эту неделю':
            if self.__database.user_exist(user_id):
                message = ''
                for i in range(6):
                    message += self.__schedule.get_day_schedule(self.__database.get_user_last_group(user_id),
                                                                - datetime.today().weekday() + i)
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Расписание на следующую неделю
        elif text == 'на следующую неделю':
            if self.__database.user_exist(user_id):
                message = ''
                for i in range(6):
                    message += self.__schedule.get_day_schedule(self.__database.get_user_last_group(user_id),
                                                                7 - datetime.today().weekday() + i)
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Меню погоды
        elif text == 'погода':
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Сейчас', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Завтра', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('На 5 дней', color=VkKeyboardColor.POSITIVE)
            return Response('Показать погоду в Москве', keyboard=keyboard)

        # Погода сейчас
        elif text == 'сейчас':
            return Weather.get_now('Москва')

        # Погода сегодня
        elif text == 'сегодня':
            return Weather.get_today('Москва')

        # Погода на завтра
        elif text == 'завтра':
            return Response('TODO')

        # Погода на 5 дней
        elif text == 'на 5 дней':
            return Response('TODO')

        # Коронавирус
        elif text == 'коронавирус' or text == 'ковид':
            return Response(message=self.__coronavirus.get_message(), image=self.__coronavirus.get_image())

        else:
            return Response('Неизвестная команда')

    @staticmethod
    def get_keyboard_schedule(message):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('На сегодня', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('На завтра', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('На эту неделю', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('На следующую неделю', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Какая неделя?')
        keyboard.add_button('Какая группа?')
        return Response(message, keyboard)
