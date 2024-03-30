import logging
import os
import sys
import time
from typing import Dict, List
from logging import StreamHandler
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram.error import TelegramError

from exceptions import (
    StatusDidNotChangeError,
    EndpointError,
    TokensNotPresentError,
    UnexpectedNameError,
    UnexpectedStatusError
)

from check_tokens_and_hw_statuses import (
    check_each_token,
    compare_statuses,
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
    """Проверяет наличие необходимых токенов."""
    try:
        check_each_token((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))
    except TokensNotPresentError as e:
        logger.critical(e)
        sys.exit()


def send_message(bot, message):
    """Отправляет сообщение через бота в чат Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError as e:
        logger.exception(e)
    logger.debug(f'Сообщение отправлено: {message}')


def get_api_answer(timestamp):
    """Получает ответ от API на основе временной метки."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise EndpointError(f'Сбой в работе программы: Эндпоинт'
                                f' {ENDPOINT} недоступен.'
                                f' Код ответа API: "{response.status_code}"'
                                f' Адрес запроса: {response.url},'
                                f' Параметры запроса: {params}')

    except requests.RequestException:
        pass

    return response.json()


def check_response(response: Dict) -> List:
    """Проверяет ответ от API и возвращает выполненное задание."""
    if not isinstance(response, dict):
        raise TypeError('Неверный тип данных от API')
    homeworks = response.get('homeworks')

    if homeworks is None:
        raise KeyError('Ключи отстутствуют в ответе')
    if not isinstance(homeworks, list):
        raise TypeError('Неверный тип данных')

    return homeworks


def parse_status(homework):
    """Возвращает сообщение о статусе выполненного домашнего задания."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS.keys():
        raise UnexpectedStatusError(f'Сбой в работе программы: Статуса '
                                    f'"{status}" не существует'
                                    f' в ответе запроса')
    if homework_name is None:
        raise UnexpectedNameError(f'Сбой в работе программы: '
                                  f'Работы с таким именем '
                                  f'"{homework_name}" не существует'
                                  f' в ответе запроса')

    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    error_message_not_sent = True
    status_before = None

    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response_content = get_api_answer(timestamp)
            homeworks = check_response(response_content)
            current_status = homeworks[0].get('status')
            message = parse_status(homeworks[0])

            compare_statuses(status_before, current_status)
            status_before = current_status

            timestamp = int(time.time())

            send_message(bot, message)

        except StatusDidNotChangeError as e:
            logger.debug(e)
            send_message(bot, str(e))

        except IndexError:
            logger.exception('Вернулся пустой массив с homeworks')
            send_message(bot, 'Не нашли твою домашку')

        except Exception as e:
            logger.exception(e)
            if error_message_not_sent:
                send_message(bot, str(e) + '\U0001F198')
                error_message_not_sent = False

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
