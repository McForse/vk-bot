import math
import requests
from utils import Utils
import PIL.Image as Image
from datetime import datetime, timedelta
from response import Response

from config import weather_path as path, owm_api_key as key


class Weather:
    url = 'http://api.openweathermap.org/data/2.5/{}?q={}&appid={}&units=metric&lang=ru'

    icons_path = path + 'icons/'

    main = {'Thunderstorm': 'гроза', 'Drizzle': 'изморось', 'Rain': 'дождь', 'Snow': 'снег', 'Mist': 'дымка',
            'Smoke': 'дымка', 'Haze': 'мгла', 'Dust': 'Пыль', 'Fog': 'туман', 'Sand': 'песок', 'Ash': 'пепел',
            'Squall': 'вихрь', 'Tornado': 'ураган', 'Clear': 'ясно', 'Clouds': 'облачно'}

    Beaufort_scale = ['штиль', 'тихий', 'лёгкий', 'слабый', 'умеренный', 'свежий', 'сильный', 'крепкий',
                      'очень крепкий', 'шторм', 'сильный шторм', 'жестокий шторм', 'ураган']

    Rumb = ['северный', 'северо-восточный', 'восточный', 'юго-восточный', 'южный', 'юго-западный', 'западный',
            'севео-западный']

    @staticmethod
    def get_json(w_type, city):
        u = Weather.url.format(w_type, city, key)
        return requests.get(u).json()

    @staticmethod
    def get_now(city):
        data = Weather.get_json('weather', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        title = 'Погода в {}: {}\n'.format(Utils.prepositional(city), Weather.main[data['weather'][0]['main']])
        message = Weather.data_message(data)
        return Response(message=message, image=Weather.icons_path + '{}.png'.format(data['weather'][0]['icon']), title=title)

    @staticmethod
    def get_today(city):
        data = Weather.get_json('forecast', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        time = ['НОЧЬ', 'УТРО', 'ДЕНЬ', 'ВЕЧЕР']
        fill = [False] * 4
        img = []
        temp = ''

        data = data['list']
        message = ''

        for weather in data:
            hour = datetime.fromtimestamp(weather['dt']).hour
            ind = None

            if hour <= 3:
                ind = 0
            elif 6 <= hour <= 9:
                ind = 1
            elif 12 <= hour <= 15:
                ind = 2
            elif 18 <= hour <= 21:
                ind = 3

            if fill[ind]:
                continue
            fill[ind] = True

            img.append(Weather.icons_path + '{}.png'.format(weather['weather'][0]['icon']))
            temp += '/ {}°C /'.format(int(weather['main']['temp_min'] + weather['main']['temp_max']) // 2)
            message += '{}\n// {}\n'.format(time[ind], Weather.data_message(weather).replace('\n', '\n// '))

            if len(set(fill)) == 1:
                break

        title = 'Погода в {} сегодня'.format(Utils.prepositional(city))
        message = '{}\n\n{}'.format(temp, message)
        return Weather.save_and_send(title, message, img)

    @staticmethod
    def get_tomorrow(city):
        data = Weather.get_json('forecast', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        time = ['НОЧЬ', 'УТРО', 'ДЕНЬ', 'ВЕЧЕР']
        fill = [False] * 4
        img = []
        temp = ''

        now_day = datetime.now().replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(days=1)
        data = data['list']
        message = ''

        for weather in data:
            date = datetime.fromtimestamp(weather['dt'])
            if date < now_day:
                continue

            hour = date.hour
            ind = None

            if hour <= 3:
                ind = 0
            elif 6 <= hour <= 9:
                ind = 1
            elif 12 <= hour <= 15:
                ind = 2
            elif 18 <= hour <= 21:
                ind = 3

            if fill[ind]:
                continue
            fill[ind] = True

            img.append(Weather.icons_path + '{}.png'.format(weather['weather'][0]['icon']))
            temp += '/ {}°C /'.format(int(weather['main']['temp_min'] + weather['main']['temp_max']) // 2)
            message += '{}\n// {}\n'.format(time[ind], Weather.data_message(weather).replace('\n', '\n// '))

            if len(set(fill)) == 1:
                break

        title = 'Погода в {} завтра'.format(Utils.prepositional(city))
        message = '{}\n\n{}'.format(temp, message)
        return Weather.save_and_send(title, message, img)

    @staticmethod
    def get_5_days(city):
        data = Weather.get_json('forecast', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        data = data['list']
        current = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        last = current + timedelta(days=6)
        title = 'Погода в {} с {} по {}\n\n'.format(Utils.prepositional(city), current.strftime('%d.%m'), last.strftime('%d.%m'))

        day = []
        night = []
        img = []

        day_temp = None
        night_temp = None
        icon = None

        for weather in data:
            date = datetime.fromtimestamp(weather['dt'])
            if date > last:
                break
            if current + timedelta(days=1) < date:
                day.append(day_temp)
                night.append(night_temp)
                img.append(icon)
                day_temp = None
                night_temp = None
                icon = None
                current = current + timedelta(days=1)
            else:
                hours = date.hour

                if hours < 7:
                    if night_temp is None or night_temp < weather['main']['temp_min']:
                        night_temp = weather['main']['temp_min']
                        if icon is None:
                            icon = Weather.icons_path + '{}.png'.format(weather['weather'][0]['icon'])
                else:
                    if day_temp is None or day_temp < weather['main']['temp_max']:
                        day_temp = weather['main']['temp_max']
                        icon = Weather.icons_path + '{}.png'.format(weather['weather'][0]['icon'])

        message = ''

        for d in day:
            if d is None:
                message += '/ ---- /'
            else:
                message += '/ {:>2}°C /'.format(math.ceil(d))
        message += ' ДЕНЬ\n'
        for n in night:
            if n is None:
                message += '/ ---- /'
            else:
                message += '/ {:>2}°C /'.format(math.trunc(n))
        message += ' НОЧЬ\n'

        return Weather.save_and_send(title, message, img, 250)

    @staticmethod
    def data_message(data):
        message = '{}, температура: {} - {}°C\nДавление: {} мм рт. ст., влажность: {}%\nВетер: {}, {} м/c, {}'.format(
            str(data['weather'][0]['description']).capitalize(), math.trunc(data['main']['temp_min']), math.ceil(data['main']['temp_max']),
            Weather.Pa_mmHg(data['main']['pressure']), data['main']['humidity'],
            Weather.Beaufort_scale[round(data['wind']['speed'])], round(data['wind']['speed']),
            Weather.deg_direction(data['wind']['deg']))
        return message

    @staticmethod
    def save_and_send(title, message, img, width=200):
        new_image = Image.new("RGBA", (width, 50))
        c = 0
        for i in img:
            img2 = Image.open(i)
            new_image.paste(img2, (c, 0))
            c += 50
        import random
        import string
        image_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        new_image.save("{}temp/{}.png".format(path, image_name))
        return Response(message, image="{}temp/{}.png".format(path, image_name), title=title)

    @staticmethod
    def Pa_mmHg(pa):
        return round(pa * 0.750063755419211)

    @staticmethod
    def deg_direction(deg):
        return Weather.Rumb[round(deg / 45) % 8]
