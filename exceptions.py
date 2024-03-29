TOKEN_NAMES = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']


class TokenNotPresentError(Exception):
    pass


class EndpointError(Exception):
    pass


class KeysResponseError(Exception):
    pass


class UnexpectedStatusError(Exception):
    pass


class UnexpectedNameError(Exception):
    pass


class StatusDidNotChangeError(Exception):
    pass


def compare_statuses(status_before, status_after):
    if status_before == status_after:
        raise StatusDidNotChangeError(f'Статус работы не изменился...'
                                      f'Все еще "{status_after}"\uE108')


def check_each_token(tokens: list):
    for token, token_name in zip(tokens, TOKEN_NAMES):
        if token is None:
            raise TokenNotPresentError(f'Отсутствует обязательная '
                                       f'переменная окружения: "{token_name}".'
                                       f'Программа принудительно'
                                       f' остановлена')

