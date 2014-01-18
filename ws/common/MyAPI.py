from flask_restful import Api
from flask_restful.utils import error_data


class MyApi(Api):
    """
    This error handler transform every flask-restful 400 error in a 412.
    """
    def handle_error(self, e):
        code = getattr(e, 'code', 500)
        data = getattr(e, 'data', error_data(code))
        if code == 400:
            r = self.make_response({'error': data}, 412)
            r.headers['Content-type'] = 'application/json'
            return r
        return super(Api, self).handle_error(e)