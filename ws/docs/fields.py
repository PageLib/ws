from flask_restful import fields
from ws.common.IsoDateTime import IsoDateTime

doc_fields = {
    'id': fields.String,
    'name': fields.String,
    'user_id': fields.String,
    'date_time': IsoDateTime,
}
