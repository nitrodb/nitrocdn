from quart import jsonify


class Err(Exception):
    resp_type = 500
    resp_message = 'Internal Server Error'

    def _to_json(self):
        return jsonify({'code': 0, 'message': f'{self.resp_type}: {self.resp_message}'})


class Forbidden(Err):
    resp_type = 403
    resp_message = 'Forbidden'


class BadData(Err):
    resp_type = 400
    resp_message = 'Bad Request'


class Unauthorized(Err):
    resp_type = 401
    resp_message = 'Unauthorized'


class NotFound(Err):
    resp_type = 404
    resp_message = 'Not Found'
