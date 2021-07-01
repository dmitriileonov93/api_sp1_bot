import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
timestamp = {'current': int(time.time())}
sleep_time = 20 * 60

logging.basicConfig(
    filename='main.log', filemode='w',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    level=logging.DEBUG)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.info('"homework_name" нет данных!')
    status = homework.get('status')
    if status is None:
        logging.info('"status" нет данных!')
    homework_statuses = {
        'reviewing': f'Ваша работа "{homework_name}" взята в ревью!',
        'rejected': f'У вас проверили работу "{homework_name}"!\n\n'
                    'К сожалению, в работе нашлись ошибки.',
        'approved': f'У вас проверили работу "{homework_name}"!\n\n'
                    'Ревьюеру всё понравилось, работа зачтена!'}
    return homework_statuses.get(status)


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time()) - sleep_time
    payload = {'from_date': current_timestamp}
    try:
        return requests.get(
            url,
            headers=headers,
            params=payload
        ).json()
    except Exception as e:
        logging.error(e)
        return e


def send_message(message):
    logging.info(f'Отправлено сообщение в тг: {message}')
    return bot.send_message(CHAT_ID, message)


def main():
    logging.debug('Бот запущен!')
    while True:
        try:
            logging.debug('отправлен запрос')
            homework_statuses = get_homeworks(timestamp['current'])
            timestamp['current'] = homework_statuses.get('current_date')
            if timestamp['current'] is None:
                logging.info('"current_date" нет данных!')
            if homework_statuses.get('homeworks'):
                homework = homework_statuses['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
            else:
                logging.debug('В "homeworks" нет данных')
            time.sleep(sleep_time)

        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logging.error(error_message)
            print(error_message)
            send_message(error_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
