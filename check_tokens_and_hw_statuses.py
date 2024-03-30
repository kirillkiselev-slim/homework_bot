from typing import Tuple
from exceptions import StatusDidNotChangeError, TokensNotPresentError

TOKEN_NAMES = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')


def compare_statuses(status_before, status_after):
    """Проверяет, изменился ли статус выполнения задания."""
    if status_before == status_after:
        raise StatusDidNotChangeError(f'Статус работы не изменился...'
                                      f'Все еще "{status_after}"\uE108')


def check_each_token(tokens: Tuple[str]):
    """Проверяет наличие каждого токена."""
    for token, token_name in zip(tokens, TOKEN_NAMES):
        if token is None:
            raise TokensNotPresentError(f'Отсутствует обязательная '
                                       f'переменная окружения: "{token_name}".'
                                       f'Программа принудительно'
                                       f' остановлена')