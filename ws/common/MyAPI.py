from flask_restful import Api


class MyApi(Api):
    def handle_error(self, e):
        """Transform a Flask-RESTful parsing error (HTTP 400) in a 412 with the inner error
            message."""
        if hasattr(e, 'code') and hasattr(e, 'data'):
            if e.code == 400 and ('message' in e.data):
                r = self.make_response({'error': e.data['message']}, 412)
                r.headers['Content-type'] = 'application/json'
                return r
        return Api.handle_error(self, e)
