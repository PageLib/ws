# -*- coding: utf-8 -*-

from functools import wraps
import json


def json_response(func):
    """
    Decorator for Flask routes returning JSON data.
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        r = func(*args, **kwargs)
        if type(r) is tuple:  # r = dict, status [, headers]
            data = r[0]
            status = r[1]
            headers = r[2] if len(r) == 3 else {}
            if type(data) is dict:
                headers.update({'Content-type': 'application/json'})
                return json.dumps(data), status, headers
            else:
                return data, status, headers
        else:
            return r

    return wrapped_func
