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

logging.basicConfig(
    filename='main.log', filemode='w',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    level=logging.DEBUG)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if status == 'reviewing':
        return f'Ваша работа "{homework_name}" взята в ревью!'
    else:
        if status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    return requests.get(
        url,
        headers=headers,
        params=payload
    ).json()


def send_message(message):
    logging.info(f'Отправлено сообщение в тг: {message}')
    return bot.send_message(CHAT_ID, message)


timestamp = {'current': int(time.time())}


def main():
    logging.debug('Бот запущен!')
    while True:
        try:
            homework_statuses = get_homeworks(timestamp['current'])
            timestamp['current'] = homework_statuses['current_date']
            if homework_statuses['homeworks']:
                homework = homework_statuses['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
            else:
                pass
            time.sleep(20 * 60)

        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logging.error(error_message)
            print(error_message)
            send_message(error_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
