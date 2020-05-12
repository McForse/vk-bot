import os
import re
import xlrd
import json
import locale
import requests
from bs4 import BeautifulSoup
from copy import deepcopy as copy
from datetime import datetime, timedelta

import config


class Schedule:

    def __init__(self):
        self.__courses_count = 0
        self.__professors = {}
        self.update()
        self.__schedule = self.get()

    def update(self):
        self.get_files()
        self.get_data()
        self.__schedule = self.get()
        self.save_professors()

    def get_files(self):
        if not os.path.exists(config.schedule_tables_path):
            os.makedirs(config.schedule_tables_path)

        page = requests.get(config.web_schedule_link)
        soup = BeautifulSoup(page.text, 'html.parser')

        result = soup.find('div', {'class': 'rasspisanie'}). \
            find(string=config.institute). \
            find_parent('div'). \
            find_parent('div'). \
            findAll('a', attrs={'href': re.compile(config.REGEX_FILE)})

        links = []

        for link in result:
            links.append(link.get('href'))

        self.__courses_count = len(links)

        for i in range(self.__courses_count):
            f = open(config.schedule_tables_path + str(i + 1) + '.xlsx', 'wb')
            resp = requests.get(links[i])
            f.write(resp.content)

    def get_courses_count(self):
        return self.__courses_count

    def get_data(self):
        groups_list = []
        groups = {}

        for course in range(self.__courses_count):
            book = xlrd.open_workbook(config.schedule_tables_path + str(course + 1) + '.xlsx')
            sheet = book.sheet_by_index(0)

            num_cols = sheet.ncols

            for col_index in range(num_cols):
                group_cell = str(sheet.cell(1, col_index).value)

                if re.search(config.REGEX_GROUP, group_cell):
                    groups_list.append(group_cell)
                    week = {'MON': None, 'TUE': None, 'WED': None, 'THU': None, 'FRI': None, 'SAT': None}

                    for k in range(6):
                        day = [[], [], [], [], [], []]

                        for i in range(6):
                            for j in range(2):
                                subject = sheet.cell(3 + j + i * 2 + k * 12, col_index).value
                                lesson_type = sheet.cell(3 + j + i * 2 + k * 12, col_index + 1).value
                                lecturer = sheet.cell(3 + j + i * 2 + k * 12, col_index + 2).value
                                classroom = sheet.cell(3 + j + i * 2 + k * 12, col_index + 3).value
                                url = sheet.cell(3 + j + i * 2 + k * 12, col_index + 4).value
                                lesson = {'subject': self.normalize_string(subject),
                                          'lesson_type': self.normalize_string(lesson_type),
                                          'lecturer': self.normalize_string(lecturer),
                                          'classroom': self.normalize_string(classroom),
                                          'url': self.normalize_string(url)}
                                day[i].append(lesson)

                                professors_list = lecturer.split('\n')
                                subject_list = subject.split('\n')
                                pr_lesson = copy(lesson)
                                pr_lesson.pop('lecturer')
                                pr_lesson['group'] = group_cell

                                for h in range(len(professors_list)):
                                    if len(subject_list) > h:
                                        pr_lesson['subject'] = subject_list[h]
                                    self.set_professor(professors_list[h], pr_lesson, config.week_days[k], i, j)

                        week[config.week_days[k]] = day

                    groups.update({group_cell: week})

        file = open(config.json_schedule_path, 'w')
        file.write(json.dumps(groups, ensure_ascii=False, indent=4))
        file.close()

    def set_professor(self, name, lesson, week_day, coup, w_type):
        if name not in self.__professors:
            day = [[None] * 2, [None] * 2, [None] * 2, [None] * 2, [None] * 2, [None] * 2]
            week = {'MON': copy(day), 'TUE': copy(day), 'WED': copy(day), 'THU': copy(day), 'FRI': copy(day),
                    'SAT': copy(day)}
            self.__professors.update({name: week})

        self.__professors[name][week_day][coup][w_type] = lesson

    def save_professors(self):
        file = open(config.json_professors_path, 'w')
        file.write(json.dumps(self.__professors, ensure_ascii=False, indent=4))
        file.close()

    def find_professors_by_last_name(self, last_name):
        return [key for key, value in self.__professors.items() if key.startswith(last_name)]

    @staticmethod
    def get():
        if config.json_schedule_path:
            with open(config.json_schedule_path, 'r') as file:
                return json.load(file)

    @staticmethod
    def normalize_string(text):
        return text.replace('\n', ' ')

    def get_day_schedule(self, group, days=0, week_day=''):
        if week_day == '':
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            data = datetime.today() + timedelta(days=days)
            week_day = data.strftime('%a').upper()
        else:
            data_offset = config.week_days.index(week_day) - datetime.today().weekday()
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

    def get_professor_schedule(self, name, days=0):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        data = datetime.today() + timedelta(days=days)
        week_day = data.strftime('%a').upper()
        week_number = self.get_study_week_number(days)
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        message = 'Расписание преподавателя {} на {} {} ({}):\n'.format(name, data.day, data.strftime('%B'), data.strftime('%A'))

        if week_day == 'SUN':
            message += 'Занятий нет\n\n'
            return message

        day = self.__professors[name][week_day]

        for couple in range(6):
            subject = day[couple][(week_number + 1) % 2]
            message += str(couple + 1) + ') '

            if subject is not None:
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
                    if subject['group']:
                        message += subject['group'] + ', '
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

    def group_exist(self, group):
        return group in self.__schedule

    def professor_exist(self, professor):
        return professor in self.__professors

    @staticmethod
    def get_study_week_number(days=0):
        month = (datetime.today() + timedelta(days=days)).month
        week_number = (datetime.today() + timedelta(days=days)).isocalendar()[1]

        if month >= 9:
            return week_number - 35
        elif month <= 1:
            return week_number + 17
        else:
            return week_number - 6
