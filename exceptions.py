TOKEN_NAMES = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
EXPECTED_KEY_HW_NAMES = ['id', 'status', 'homework_name', 'reviewer_comment',
                         'date_updated', 'lesson_name']
STATUSES = ['approved', 'reviewing', 'rejected']


class TokenNotPresentError(Exception):
    pass


def check_each_token(tokens: list):
    for token, token_name in zip(tokens, TOKEN_NAMES):
        if token is None:
            raise TokenNotPresentError(f'Отсутствует обязательная '
                                       f'переменная окружения: "{token_name}"'
                                       f' Программа принудительно'
                                       f' остановлена.')


class EndpointError(Exception):
    pass


def check_endpoint_availability(endpoint, response):
    if response.status_code != 200:
        raise EndpointError(f'Сбой в работе программы: Эндпоинт'
                            f' {endpoint} недоступен.'
                            f' Код ответа API: "{response.status_code}" ')


class KeysResponseError(Exception):
    pass


def check_keys_in_homework(homework):
    for received_key, expected_key in zip(homework.keys(),
                                          EXPECTED_KEY_HW_NAMES):
        if received_key != expected_key:
            raise KeysResponseError(f'Сбой в работе программы: Ключ '
                                    f'{expected_key} не равен '
                                    f'ключу {received_key}')


class UnexpectedStatusError(Exception):
    pass


def check_received_status(homework):
    status = homework.get('status')
    if status not in STATUSES:
        raise UnexpectedStatusError(f'Сбой в работе программы: Статуса '
                                    f'{status} не существует'
                                    f' в ответе запроса')
    else:
        return status


class StatusDidNotChangeError(Exception):
    pass


def compare_statuses(status_before, status_after):
    if status_before == status_after:
        raise StatusDidNotChangeError(f'Статус работы "{status_after}"'
                                      f' не изменился :(')
