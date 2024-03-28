from datetime import datetime, timedelta
import logging
import os
import sys
import time
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv
import schedule

from homework_bot.exceptions import (
    check_each_token,
    check_endpoint_availability,
    EndpointError,
    TokenNotPresentError,
    check_keys_in_homework,
    KeysResponseError,
    check_received_status,
    UnexpectedStatusError,
    compare_statuses,
    StatusDidNotChangeError
)

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
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
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
        sys.exit()


def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.debug(message)


def get_api_answer(timestamp):
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return response


def check_response(response):
    return response.json().get('homeworks')[0]


def parse_status(homework):
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS[homework.get('status')]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    now = datetime.today()

    days_30 = now - timedelta(days=60)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(days_30.timestamp())  # int(time.time())

    scheduled_message = schedule.every(10).seconds.do
    status_before = None

    while True:
        schedule.run_pending()
        time.sleep(1)
        try:
            response = get_api_answer(timestamp)
            check_endpoint_availability(ENDPOINT, response)

            homework = check_response(response)
            check_keys_in_homework(homework)

            current_status = check_received_status(homework)
            compare_statuses(status_before, current_status)
            status_before = current_status

            message = parse_status(homework)
            scheduled_message(send_message, bot, message)

        except (EndpointError, KeysResponseError,
                UnexpectedStatusError) as e:
            schedule.every(10).seconds.do(logger.error, str(e))

            send_message(bot, str(e))

        except StatusDidNotChangeError as e:
            schedule.every(10).seconds.do(logger.debug, str(e))

            scheduled_message(send_message, bot, str(e))


if __name__ == '__main__':
    main()
