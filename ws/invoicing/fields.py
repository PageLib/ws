from flask_restful import fields
__author__ = 'Alexis'

transaction_fields = {
    'user':  fields.String,
    'amount': fields.Float,
    'date_time': fields.DateTime,
    'currency': fields.String,
    'type': fields.String
}
printing_fields = {
    'pages_color': fields.Integer,
    'pages_grey_level': fields.Integer,
    'copies': fields.Integer
}
printing_fields.update(transaction_fields)

loading_credit_card_fields = transaction_fields
help_desk_fields = transaction_fields