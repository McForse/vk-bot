import json
import requests
from utils import Utils

from config import owm_api_key as key


class Weather:
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang=ru'
    temp = '{"coord":{"lon":37.62,"lat":55.75},"weather":[{"id":804,"main":"Clouds","description":"пасмурно","icon":"04n"}],"base":"stations","main":{"temp":12.66,"feels_like":10.25,"temp_min":12,"temp_max":13,"pressure":1008,"humidity":62},"visibility":10000,"wind":{"speed":2,"deg":350},"clouds":{"all":100},"dt":1589053952,"sys":{"type":1,"id":9027,"country":"RU","sunrise":1588987736,"sunset":1589044980},"timezone":10800,"id":524901,"name":"Москва","cod":200}'

    main = {'Thunderstorm': 'гроза', 'Drizzle': 'изморось', 'Rain': 'дождь', 'Snow': 'снег', 'Mist': 'дымка', 'Smoke': 'дымка', 'Haze': 'мгла', 'Dust': 'Пыль', 'Fog': 'туман', 'Sand': 'песок', 'Ash': 'пепел', 'Squall': 'вихрь', 'Tornado': 'ураган', 'Clear': 'ясно', 'Clouds': 'облачно'}

    description = {'clear sky': 'ясное небо', 'few clouds': 'малооблачно', 'scattered clouds': 'рассеянные облака', 'broken clouds': 'облачность'}

    Beaufort_scale = ['штиль', 'тихий', 'лёгкий', 'слабый', 'умеренный', 'свежий', 'сильный', 'крепкий',
                      'очень крепкий', 'шторм', 'сильный шторм', 'жестокий шторм', 'ураган']

    Rumb = ['северный', 'северо-восточный', 'восточный', 'юго-восточный', 'южный', 'юго-западный', 'западный', 'севео-западный']

    @staticmethod
    def get_json(city):
        # return requests.get(Weather.url.format(city, key)).json()
        return json.loads(Weather.temp)

    @staticmethod
    def get_message(city):
        data = Weather.get_json(city)

        if 'cod' not in data or data['cod'] != 200:
            return 'Произошла ошибка при получении погоды'

        city_name = Utils.prepositional(city)

        message = 'Погода в {}: {}\n{}, температура: {} - {}°C\nДавление: {} мм рт. ст., влажность: {}%\nВетер: {}, {} м/c, {}'.format(
            city_name, Weather.main[data['weather'][0]['main']],
            str(data['weather'][0]['description']).capitalize(), data['main']['temp_min'], data['main']['temp_max'],
            Weather.Pa_mmHg(data['main']['pressure']), data['main']['humidity'],
            Weather.Beaufort_scale[data['wind']['speed']], data['wind']['speed'],
            Weather.deg_direction(data['wind']['deg']))
        return message

    @staticmethod
    def Pa_mmHg(pa):
        return round(pa * 0.750063755419211)

    @staticmethod
    def deg_direction(deg):
        return Weather.Rumb[round(deg / 45) % 8]
