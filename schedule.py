import os
import re
import xlrd
import json
import requests
from bs4 import BeautifulSoup

import config


class Schedule:

    def __init__(self):
        self.__courses_count = 0
        self.get_files()
        self.get_data()

    def get_files(self):
        if not os.path.exists(config.excel_tables_path):
            os.makedirs(config.excel_tables_path)

        page = requests.get(config.web_schedule_link)
        soup = BeautifulSoup(page.text, 'html.parser')

        result = soup.find("div", {"class": "rasspisanie"}). \
            find(string=config.institute). \
            find_parent("div"). \
            find_parent("div"). \
            findAll('a', attrs={'href': re.compile(config.REGEX_FILE)})

        links = []

        for link in result:
            links.append(link.get('href'))

        self.__courses_count = len(links)

        for i in range(self.__courses_count):
            f = open(config.excel_tables_path + str(i + 1) + ".xlsx", "wb")
            resp = requests.get(links[i])
            f.write(resp.content)

    def get_courses_count(self):
        return self.__courses_count

    def get_data(self):
        groups_list = []
        groups = {}
        week_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]

        for course in range(self.__courses_count):
            book = xlrd.open_workbook(config.excel_tables_path + str(course + 1) + ".xlsx")
            sheet = book.sheet_by_index(0)

            num_cols = sheet.ncols

            for col_index in range(num_cols):
                group_cell = str(sheet.cell(1, col_index).value)

                if re.search(config.REGEX_GROUP, group_cell):
                    groups_list.append(group_cell)
                    week = {"MON": None, "TUE": None, "WED": None, "THU": None, "FRI": None, "SAT": None}

                    for k in range(6):
                        day = [[], [], [], [], [], []]

                        for i in range(6):
                            for j in range(2):
                                subject = sheet.cell(3 + j + i * 2 + k * 12, col_index).value
                                lesson_type = sheet.cell(3 + j + i * 2 + k * 12, col_index + 1).value
                                lecturer = sheet.cell(3 + j + i * 2 + k * 12, col_index + 2).value
                                classroom = sheet.cell(3 + j + i * 2 + k * 12, col_index + 3).value
                                url = sheet.cell(3 + j + i * 2 + k * 12, col_index + 4).value
                                lesson = {"subject": Schedule.normalize_string(subject),
                                          "lesson_type": Schedule.normalize_string(lesson_type),
                                          "lecturer": Schedule.normalize_string(lecturer),
                                          "classroom": Schedule.normalize_string(classroom),
                                          "url": Schedule.normalize_string(url)
                                          }
                                day[i].append(lesson)

                        week[week_days[k]] = day

                    groups.update({group_cell: week})

        file = open(config.json_data_path, "w")
        file.write(json.dumps(groups, ensure_ascii=False, indent=4))
        file.close()

    @staticmethod
    def get():
        if config.json_data_path:
            with open(config.json_data_path, 'r') as file:
                return json.load(file)

    @staticmethod
    def normalize_string(text):
        return text.replace('\n', ' ')
