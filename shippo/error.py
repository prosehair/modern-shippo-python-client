# Exceptions
class ShippoError(Exception):
    def __init__(self, message, http_body=None, http_status=None, json_body=None):
        super().__init__(message)
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body


class APIError(ShippoError):
    pass


class APIConnectionError(ShippoError):
    pass


class ConfigurationError(ShippoError):
    pass


class AddressError(ShippoError):
    def __init__(self, message, param, code, http_body=None, http_status=None, json_body=None):
        super().__init__(message, http_body, http_status, json_body)
        self.param = param
        self.code = code


class InvalidRequestError(ShippoError):
    def __init__(self, message, param, http_body=None, http_status=None, json_body=None):
        super().__init__(message, http_body, http_status, json_body)
        self.param = param


class AuthenticationError(ShippoError):
    pass
