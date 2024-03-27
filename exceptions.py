NAMES_TOKENS = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']


class TokenNotPresentError(Exception):
    pass


def check_each_token(tokens: list):
    for token, name_token in zip(tokens, NAMES_TOKENS):
        if token is None:
            raise TokenNotPresentError(f'Отсутствует обязательная '
                                       f'переменная окружения: "{name_token}"'
                                       f' Программа принудительно'
                                       f' остановлена.')


class EndpointError(Exception):
    pass


def check_endpoint_availability(endpoint, response):
    if response.status_code != 200:
        raise EndpointError(f'Сбой в работе программы: Эндпоинт'
                            f' {endpoint} недоступен.'
                            f' Код ответа API: {response.status_code}" ')
