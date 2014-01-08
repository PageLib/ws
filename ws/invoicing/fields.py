from flask_restful import fields
__author__ = 'Alexis'


class IsoDateTime(fields.Raw):
    """Return a ISO-formatted datetime string in UTC"""

    def format(self, value):
        try:
            return value.isoformat()
        except AttributeError as ae:
            raise fields.MarshallingException(ae)


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