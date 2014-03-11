from flask_restful import fields


class IsoDateTime(fields.Raw):
    """Return a ISO-formatted datetime string in UTC"""

    def format(self, value):
        try:
            return value.isoformat()
        except AttributeError as ae:
            raise fields.MarshallingException(ae)