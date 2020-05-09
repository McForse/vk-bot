import re
import locale
from response import Response
from datetime import datetime, timedelta
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import config

REGEX_COMMAND = '^{} .*'
week_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
week_days_interpreter = {'понедельник': 'MON', 'вторник': 'TUE', 'среда': 'WED', 'четверг': 'THU', 'пятница': 'FRI',
                         'суббота': 'SAT', 'воскресенье': 'SUN'}


class Handler:

    def __init__(self, database, schedule):
        self.__database = database
        self.__schedule = schedule

    def handle(self, user_id, text):

        # Установка группы
        if re.search(config.REGEX_GROUP, text.upper()):
            group = text.upper()

            if group in self.__schedule:
                self.__database.set_user_group(user_id, text.upper())
                return Response('Я запомнил, что ты из группы ' + group)
            else:
                return Response('Такой группы нет')

        # Номер группы
        elif text == 'какая группа?':
            if self.__database.exist_user(user_id):
                return Response('Показываю расписание группы {}'.format(self.__database.get_user_group(user_id)))
            else:
                return Response('Я не знаю в какой вы группе')

        # Номер недели
        elif text == 'какая неделя?':
            return Response('Идёт {} неделя'.format(self.get_study_week_number()))

        # Меню с расписанием с дополнительными параметрами
        elif re.search(REGEX_COMMAND.format('бот'), text):
            commands = text.split()

            # Расписание на определённый день недели
            if commands[1] in week_days_interpreter:

                # Для конкретной группы
                if len(commands) == 3:
                    group = commands[2].upper()

                    if re.search(config.REGEX_GROUP, group):
                        if group in self.__schedule:
                            message = self.get_day_schedule(group=group, week_day=week_days_interpreter[commands[1]])
                            return Response(message)
                        else:
                            return Response('Такой группы нет')
                    else:
                        return Response('Неизвестная команда')

                # Для группы пользователя
                elif len(commands) == 2:
                    if self.__database.exist_user(user_id):
                        message = self.get_day_schedule(group=self.__database.get_user_last_group(user_id),
                                                        week_day=week_days_interpreter[commands[1]])
                        return Response(message)
                    else:
                        return Response('Я не знаю в какой вы группе')
                else:
                    return Response('Неизвестная команда')

            # Меню с расписанием для конкретной группы
            elif re.search(config.REGEX_GROUP, commands[1].upper()):
                group = commands[1].upper()

                if group in self.__schedule:
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
            if self.__database.exist_user(user_id):
                message = self.get_day_schedule(self.__database.get_user_last_group(user_id))
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Расписание на завтра
        elif text == 'на завтра':
            if self.__database.exist_user(user_id):
                message = self.get_day_schedule(self.__database.get_user_last_group(user_id), 1)
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Расписание на эту неделю
        elif text == 'на неделю' or text == 'на эту неделю':
            if self.__database.exist_user(user_id):
                message = ''
                for i in range(6):
                    message += self.get_day_schedule(self.__database.get_user_last_group(user_id),
                                                     - datetime.today().weekday() + i)
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')

        # Расписание на следующую неделю
        elif text == 'на следующую неделю':
            if self.__database.exist_user(user_id):
                message = ''
                for i in range(6):
                    message += self.get_day_schedule(self.__database.get_user_last_group(user_id),
                                                     7 - datetime.today().weekday() + i)
                self.__database.remove_user_temp(user_id)
                return Response(message)
            else:
                return Response('Я не знаю в какой вы группе')
        else:
            return Response('Неизвестная команда')

    def get_day_schedule(self, group, days=0, week_day=''):
        print(group)
        if week_day == '':
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            data = datetime.today() + timedelta(days=days)
            week_day = data.strftime('%a').upper()
        else:
            data_offset = week_days.index(week_day) - datetime.today().weekday()
            data = datetime.today() + timedelta(days=data_offset)

        week_number = self.get_study_week_number(days)

        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        message = 'Расписание на {} {} ({}):\n'.format(data.day, data.strftime('%B'), data.strftime('%A'))

        if week_day == 'SUN':
            message += 'Занятий нет\n\n'
            return message

        day = self.__schedule[group][week_day]

        for couple in range(6):
            subject = day[couple][(week_number + 1) % 2]
            message += str(couple + 1) + ') '

            if subject['subject']:
                str_except = re.findall(config.REGEX_WEEKS_EXCEPT, subject['subject'])
                except_weeks = []
                only_weeks = []
                subject_name = subject['subject']

                if str_except:
                    except_weeks = str(str_except[0]).split(',')
                    subject_name = re.sub(config.REGEX_WEEKS_EXCEPT_DELETE, '', subject_name)
                else:
                    str_only = re.findall(config.REGEX_WEEKS_ONLY, subject['subject'])
                    if str_only:
                        only_weeks = str(str_only[0]).split(',')
                        subject_name = re.sub(config.REGEX_WEEKS_ONLY_DELETE, '', subject_name)

                if except_weeks and str(week_number) in except_weeks:
                    message += '-\n'
                elif only_weeks and str(week_number) not in only_weeks:
                    message += '-\n'
                else:
                    message += subject_name + ', '
                    if subject_name:
                        message += subject['lesson_type'] + ', '
                    else:
                        message += '-, '
                    if subject['lecturer']:
                        message += subject['lecturer'] + ', '
                    else:
                        message += '-, '
                    if subject['classroom']:
                        message += subject['classroom'] + '\n'
                    else:
                        message += '-\n'
                    if subject['url']:
                        message += subject['url'] + '\n'

            else:
                message += '-\n'

        message += '\n'

        return message

    def get_keyboard_schedule(self, message):
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

    def get_study_week_number(self, days=0):
        month = (datetime.today() + timedelta(days=days)).month
        week_number = (datetime.today() + timedelta(days=days)).isocalendar()[1]

        if month >= 9:
            return week_number - 35
        elif month <= 1:
            return week_number + 17
        else:
            return week_number - 6
