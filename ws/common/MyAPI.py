from flask_restful import Api
from flask_restful.utils import error_data


class MyApi(Api):
    def handle_error(self, e):
        code = getattr(e, 'code', 500)
        data = getattr(e, 'data', error_data(code))
        if code == 400:
            r = self.make_response({'error': data}, 412)
            r.headers['Content-type'] = 'application/json'
            return r
        return super(Api, self).handle_error(e) # for all other errors than 500 use flask-restful's default error handling.