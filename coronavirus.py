import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from config import covid_path


class DayStatistic:

    def __init__(self, active, active_new, cured, cured_new, dead, dead_new, cases,
                 cases_new: int):
        self.active = active
        self.active_new = active_new
        self.cured = cured
        self.cured_new = cured_new
        self.dead = dead
        self.dead_new = dead_new
        self.cases = cases
        self.cases_new = cases_new


class Encoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Coronavirus:
    url = 'https://coronavirusstat.ru/country/russia/'

    REGEX_DATES = r''
    REGEX_COL_DATA = r'\d*\.\d+|\d+'

    def __init__(self):
        self.__last_update = None
        self.__message = None

    def get_data(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.findAll('table')[0]
        table_body = table.find('tbody')

        data = {}
        rows = table_body.findAll('tr')

        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            active_data = re.findall(self.REGEX_COL_DATA, cols[0])
            cured_data = re.findall(self.REGEX_COL_DATA, cols[1])
            dead_data = re.findall(self.REGEX_COL_DATA, cols[2])
            cases_data = re.findall(self.REGEX_COL_DATA, cols[3])

            date = str(row.find('th').contents[0])
            data.update({date: DayStatistic(
                int(active_data[0]), int(active_data[1]),
                int(cured_data[0]), int(cured_data[1]),
                int(dead_data[0]), int(dead_data[1]),
                int(cases_data[0]), int(cases_data[1])
            )})

        dates = list(data.keys())
        dates.reverse()

        y1 = [data[date].active for date in dates]
        y2 = [data[date].cured for date in dates]
        y3 = [data[date].dead for date in dates]

        labels = ['Активных', 'Вылечено', 'Умерло']

        fig, ax = plt.subplots()
        ax.stackplot(dates, y1, y2, y3, labels=labels)
        ax.legend(loc='upper left')
        plt.title('Россия - детальная статистика - коронвирус')
        fig.autofmt_xdate()

        page = requests.get(self.url)
        soup = BeautifulSoup(page.text, 'html.parser')
        update = soup.find('h6').find('strong').contents[0]
        today = dates[9]

        message = 'По состоянию на {}\nСлучаев: {} (+{} за сегодня)\nАктивных: {} (+{} за сегодня)\nВылечено: {} (+{} за сегодня)\nУмерло: {} (+{} за сегодня)'.format(
            update,
            data[today].cases, data[today].cases_new,
            data[today].active, data[today].active_new,
            data[today].cured, data[today].cured_new,
            data[today].dead, data[today].dead_new
        )

        if not os.path.exists(covid_path):
            os.makedirs(covid_path)

        fig.savefig(covid_path + 'covid.png')

        file = open(covid_path + 'data.json', 'w')
        file.write(json.dumps(data, ensure_ascii=False, indent=4, cls=Encoder))
        file.close()

        self.update_info(today, message)

    def get_message(self):
        if self.__last_update is not None and self.__message is not None:
            if not self.check_update(self.__last_update):
                print('Сообщение из переменной')
                return self.__message

        if not os.path.exists(covid_path + 'info.json') or not os.path.exists(covid_path + 'covid.png'):
            print('Загрузка данных')
            self.get_data()

        file = open(covid_path + 'info.json', 'r')
        data = json.load(file)
        file.close()

        if self.check_update(str(data['last_update'])):
            print('Обновление данных')
            self.get_data()
            file = open(covid_path + 'info.json', 'r')
            data = json.load(file)
            file.close()

        self.__last_update = data['last_update']
        self.__message = data['message']
        return self.__message

    @staticmethod
    def get_image():
        if os.path.exists(covid_path + 'covid.png'):
            return covid_path + 'covid.png'

    @staticmethod
    def check_update(last_update):
        now = datetime.now() - timedelta(days=1)
        last_updated_date = datetime.strptime(last_update + ' 10:45', '%d.%m.%Y %H:%M')
        return now > last_updated_date

    @staticmethod
    def update_info(last_update, message):
        info = {'last_update': last_update, 'message': message}
        file = open(covid_path + 'info.json', 'w')
        file.write(json.dumps(info, ensure_ascii=False, indent=4))
        file.close()
