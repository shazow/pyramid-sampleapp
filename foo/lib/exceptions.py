class ListopiException(Exception):
    pass


class APIException(ListopiException):
    def __init__(self, message, code=400):
        self.message = message
        self.code = 400


class APIError(APIException):
    pass


class APIControllerError(APIError):
    pass


class LoginRequired(APIException):
    def __init__(self, next=None):
        self.message = 'Login required.'
        self.code = 403
        self.next = next
