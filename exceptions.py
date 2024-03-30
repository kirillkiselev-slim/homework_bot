class TokensNotPresentError(Exception):
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
