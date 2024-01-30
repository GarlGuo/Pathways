

class RESPONSE:
    def __init__(self, successOrNot=True, value=None, error=None, exception=None):
        self.success = successOrNot
        if self.success and not exception:
            self.value = value
        else:
            self.error = error
            self.exception = exception

    def is_successful(self):
        return self.success

    def is_unsuccessful(self):
        return not self.success

    @classmethod
    def success(cls, value=None):
        return RESPONSE(successOrNot=True, value=value)

    @classmethod
    def errors(cls, errors):
        if type(errors) == str:
            return RESPONSE(successOrNot=False, error=errors)
        else:
            return RESPONSE(successOrNot=False, error=', '.join(errors))


class HTTP_RESPONSE(RESPONSE):
    pass


class Redis_RESPONSE(RESPONSE):
    @classmethod
    def unfound(cls):
        return RESPONSE.errors("unfound")

    @classmethod
    def is_unfound(cls, response):
        if not isinstance(response, RESPONSE):
            raise ValueError(f"{type(response)} is NOT the Redis_RESPONSE type")
        return response.is_unsuccessful() and response.error == "unfound"



class DB_RESPONSE(RESPONSE):

    @classmethod
    def unsupported_operation(cls, msg=None):
        if msg is not None:
            return DB_RESPONSE(error=f'{msg} is not supported')
        else:
            return DB_RESPONSE(error=f'unsupported operation')
