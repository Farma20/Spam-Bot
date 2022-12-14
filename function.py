import re
import time
import json
from urllib.parse import urlparse


# Функция, возвращающая укороченные до домашней страницы url адреса
def return_short_urls(message):
    links_from_message = re.findall(r'(https?://[^\s]+)', message.text)
    urls_short = [urlparse(x).scheme + '://' + urlparse(x).netloc for x in links_from_message]
    return urls_short


# Функция, возвращающая данные из json
def return_data_from_json(json_path):
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
    except ValueError:
        data = {'urls': []}

    return data


# Функция, записывающая данные в json
def write_data_in_json(data, urls_short, json_path):
    if len(data) == 0:
        data = {'urls': urls_short}
    else:
        data['urls'].extend(urls_short)

    with open(json_path, 'w') as file:
        json.dump(data, file)


# Функция, ищущая совпадения в url из сообщения с url из белого списка
def find_allowed_urls(urls_short, white_list):
    if len(urls_short) == 0:
        return False
    return all(x in white_list['urls'] for x in urls_short)


# Функция, подтверждающая статус админа или создателя
def confirmation_status_user(message, bot):
    user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
    status = user_info.status
    return status in ['creator', 'administrator']


# таймер для удаления сообщений
def delete_message_timer(message, bot):
    timing_start = time.time()

    while True:
        if time.time() - timing_start >= 5:
            bot.delete_message(message.chat.id, message.message_id)
            break
