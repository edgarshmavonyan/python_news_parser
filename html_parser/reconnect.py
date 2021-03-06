from functools import wraps

RECONNECT_NUMBER = 10


def reconnect_decorator(request_function):
    """Make wrapped function reconnect several times not throwing exception
    :param request_function: function to wrap
    :return: decorated function"""
    @wraps(request_function)
    def func_wrapper(*args, **kwargs):
        counter = 0
        while True:
            try:
                counter += 1
                return request_function(*args, **kwargs)
            except ConnectionError:
                if counter >= RECONNECT_NUMBER:
                    raise ConnectionError('No connection to rbc.ru')
    return func_wrapper
