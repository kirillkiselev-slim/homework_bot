import logging
import os
import sys
import time
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from homework_bot.exceptions import check_each_token, TokenNotPresentError, check_endpoint_availability, EndpointError

load_dotenv()

logger = logging.getLogger(__name__)

logger.setLevel(level=logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)

logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)

handler.setFormatter(formatter)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    try:
        check_each_token([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
    except TokenNotPresentError as e:
        logger.critical(e)


def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.debug(message)


def get_api_answer(timestamp):
    try:
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params).json()
        check_endpoint_availability(ENDPOINT, response)
    except EndpointError as e:
        logger.error(e)


def check_response(response):
    return response[0].get('homeworks')


def parse_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    get_api_answer(timestamp)

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        ...


if __name__ == '__main__':
    main()
