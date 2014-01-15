from flask_restful import fields


user_fields = {
    'id': fields.String,
    'login': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'role': fields.String
}
