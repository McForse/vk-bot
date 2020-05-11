import json
import requests
from utils import Utils
import PIL.Image as Image
from datetime import datetime
from response import Response

from config import owm_api_key as key


class Weather:
    url = 'http://api.openweathermap.org/data/2.5/{}?q={}&appid={}&units=metric&lang=ru'
    path = 'weather/'
    temp = '{"coord":{"lon":37.62,"lat":55.75},"weather":[{"id":804,"main":"Clouds","description":"пасмурно","icon":"04n"}],"base":"stations","main":{"temp":12.66,"feels_like":10.25,"temp_min":12,"temp_max":13,"pressure":1008,"humidity":62},"visibility":10000,"wind":{"speed":2,"deg":350},"clouds":{"all":100},"dt":1589053952,"sys":{"type":1,"id":9027,"country":"RU","sunrise":1588987736,"sunset":1589044980},"timezone":10800,"id":524901,"name":"Москва","cod":200}'

    main = {'Thunderstorm': 'гроза', 'Drizzle': 'изморось', 'Rain': 'дождь', 'Snow': 'снег', 'Mist': 'дымка',
            'Smoke': 'дымка', 'Haze': 'мгла', 'Dust': 'Пыль', 'Fog': 'туман', 'Sand': 'песок', 'Ash': 'пепел',
            'Squall': 'вихрь', 'Tornado': 'ураган', 'Clear': 'ясно', 'Clouds': 'облачно'}

    Beaufort_scale = ['штиль', 'тихий', 'лёгкий', 'слабый', 'умеренный', 'свежий', 'сильный', 'крепкий',
                      'очень крепкий', 'шторм', 'сильный шторм', 'жестокий шторм', 'ураган']

    Rumb = ['северный', 'северо-восточный', 'восточный', 'юго-восточный', 'южный', 'юго-западный', 'западный',
            'севео-западный']

    @staticmethod
    def get_json(w_type, city):
        return requests.get(Weather.url.format(w_type, city, key)).json()
        # return json.loads(Weather.temp)

    @staticmethod
    def get_now(city):
        data = Weather.get_json('weather', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        message = 'Погода в {}: {}\n'.format(Utils.prepositional(city), Weather.main[data['weather'][0]['main']])
        message += Weather.data_message(data)
        return Response(message=message, image=Weather.path + 'icons/' + data['weather'][0]['icon'] + '.png')

    @staticmethod
    def get_5_days(city):
        data = Weather.get_json('forecast', city)

        if 'cod' not in data or data['cod'] != 200:
            return Response('Произошла ошибка при получении погоды')
        return Response()

    @staticmethod
    def get_today(city):
        data = Weather.get_json('forecast', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        time = ['НОЧЬ', 'УТРО', 'ДЕНЬ', 'ВЕЧЕР']
        fill = [False, False, False, False]
        img = []
        temp = ''

        data = data['list']
        message = ''

        for weather in data:
            hour = datetime.fromtimestamp(weather['dt']).hour
            ind = None

            if 0 <= hour <= 3:
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

            img.append(Weather.path + 'icons/{}.png'.format(weather['weather'][0]['icon']))
            temp += '/ {}°C /'.format(int(weather['main']['temp_min'] + weather['main']['temp_max']) // 2)
            message += '{}\n// {}\n'.format(time[ind], Weather.data_message(weather).replace('\n', '\n// '))

            if len(set(fill)) == 1:
                break

        message = temp + '\n\n' + message
        return Weather.save_and_send(message, img)

    @staticmethod
    def get_tomorrow(city):
        data = Weather.get_json('forecast', city)

        if 'cod' not in data or int(data['cod']) != 200:
            return Response('Произошла ошибка при получении погоды')

        time = ["\nНОЧЬ\n", "\nУТРО\n", "\nДЕНЬ\n", "\nВЕЧЕР\n"]

        return Response()

    @staticmethod
    def data_message(data):
        message = '{}, температура: {} - {}°C\nДавление: {} мм рт. ст., влажность: {}%\nВетер: {}, {} м/c, {}'.format(
            str(data['weather'][0]['description']).capitalize(), data['main']['temp_min'], data['main']['temp_max'],
            Weather.Pa_mmHg(data['main']['pressure']), data['main']['humidity'],
            Weather.Beaufort_scale[round(data['wind']['speed'])], data['wind']['speed'],
            Weather.deg_direction(data['wind']['deg']))
        return message

    @staticmethod
    def save_and_send(message, img):
        new_image = Image.new("RGBA", (200, 50))
        c = 0
        for i in img:
            img2 = Image.open(i)
            new_image.paste(img2, (c, 0))
            c += 50
        new_image.save("{}temp/new.png".format(Weather.path))
        return Response(message, image="{}temp/new.png".format(Weather.path))

    @staticmethod
    def Pa_mmHg(pa):
        return round(pa * 0.750063755419211)

    @staticmethod
    def deg_direction(deg):
        return Weather.Rumb[round(deg / 45) % 8]


if __name__ == '__main__':
    print(Weather.get_today('Москва').message)
