from flask_restful import fields
from ws.common.IsoDateTime import IsoDateTime


transaction_fields = {
    'id': fields.String,
    'user_id':  fields.String,
    'amount': fields.Float,
    'date_time': IsoDateTime,
    'currency': fields.String,
    'transaction_type': fields.String
}

printing_fields = {
    'pages_color': fields.Integer,
    'pages_grey_level': fields.Integer,
    'copies': fields.Integer
}
printing_fields.update(transaction_fields)

loading_credit_card_fields = transaction_fields
help_desk_fields = transaction_fields
