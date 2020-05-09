import secrets

log = True

vk_api_token = secrets.vk_api_token

web_schedule_link = 'https://www.mirea.ru/schedule/'

institute = 'Институт информационных технологий'

excel_tables_path = 'schedule/tables/'

json_data_path = 'schedule/data.json'

# Регулярные выражения

REGEX_FILE = r'((^http)|(^https))://(.*?)(ИИТ_)(.*?)(.xlsx$)'
REGEX_GROUP = r'^[А-Я]{4}-[0-9]{2}-[0-9]{2}'
REGEX_WEEKS_EXCEPT = r'(?:(?<=кр. )|(?<=кр ))(.*?)(?= н.)'
REGEX_WEEKS_EXCEPT_DELETE = r'((кр. )|(кр )).*?(н. )'
REGEX_WEEKS_ONLY = r'^(?!кр.*$).*?[0-9,]+(?= н.)'
REGEX_WEEKS_ONLY_DELETE = r'^(?!кр.*$).*?[0-9,]+ (н.|н) '
