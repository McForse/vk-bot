import secrets

log = True

vk_api_token = secrets.vk_api_token

owm_api_key = secrets.owm_api_key

web_schedule_link = 'https://www.mirea.ru/schedule/'

institute = 'Институт информационных технологий'

schedule_tables_path = 'schedule/tables/'

json_schedule_path = 'schedule/data.json'

json_professors_path = 'schedule/professors.json'

weather_path = 'weather/'

covid_path = 'coronavirus/'

week_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

week_days_interpreter = {'понедельник': 'MON', 'вторник': 'TUE', 'среда': 'WED', 'четверг': 'THU', 'пятница': 'FRI',
                         'суббота': 'SAT', 'воскресенье': 'SUN'}

# Регулярные выражения

REGEX_FILE = r'((^http)|(^https))://(.*?)(ИИТ_)(.*?)(.xlsx$)'
REGEX_GROUP = r'^[А-Я]{4}-[0-9]{2}-[0-9]{2}'
REGEX_PROFESSOR = r'^([А-Яа-я]+) ([А-Яа-я]{1}).([А-Яа-я]{1}).$'
REGEX_WEEKS_EXCEPT = r'(?:(?<=кр. )|(?<=кр ))(.*?)(?= н.)'
REGEX_WEEKS_EXCEPT_DELETE = r'((кр. )|(кр )).*?(н. )'
REGEX_WEEKS_ONLY = r'^(?!кр.*$).*?[0-9,]+(?= н.)'
REGEX_WEEKS_ONLY_DELETE = r'^(?!кр.*$).*?[0-9,]+ (н.|н) '
