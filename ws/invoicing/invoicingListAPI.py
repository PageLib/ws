__author__ = 'Alexis'
from flask_restful import Resource, reqparse, marshal
from app import db
from model import Printing, LoadingCreditCard, HelpDesk
from fields import printing_fields, loading_credit_card_fields, help_desk_fields

class InvoicingListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('amount', type=int, required=True, location='json',
                                   help='No amount provided')
        self.reqparse.add_argument('transaction_type', type=str, location='json',
                                   required=True, help='No type provided')
        self.reqparse.add_argument('currency', type=str, location='json',
                                   required=True, help='No currency provided')
        self.reqparse.add_argument('user', type=str, location='json',
                                   required=True, help='No user provided')
        self.reqparse.add_argument('copies', type=int, location='json')
        self.reqparse.add_argument('pages_color', type=int, location='json')
        self.reqparse.add_argument('pages_grey_level', type=int, location='json')
        super(InvoicingListAPI, self).__init__()

    #    def get(self):
    #        return None

    def post(self):
        """
        Create a new transaction.
        """
        args = self.reqparse.parse_args()
        transaction_type = args['transaction_type']
        amount= args['amount']
        currency = args['currency']
        user = args['user']

        #If the type is not good
        if transaction_type not in ['printing', 'loading_credit_card', 'help_desk']:
            return {'error': 'Type unknown'}, 412

        if transaction_type == 'printing':
            pages_color = args['pages_color']
            copies = args['copies']
            pages_grey_level = args['pages_grey_level']
            #TODO gerer les nulls dans les pages et copies.
            t = Printing(user, amount, currency, pages_color, pages_grey_level, copies)
            db.session.add(t)
            db.session.commit()
            return marshal(t.to_dict(), printing_fields), 201
        elif transaction_type == 'loading_credit_card':
            t = LoadingCreditCard(user, amount, currency)
            db.session.add(t)
            db.session.commit()
            return marshal(t.to_dict(), loading_credit_card_fields), 201
        elif transaction_type == 'help_desk':
            t = HelpDesk(user, amount, currency)
            db.session.add(t)
            db.session.commit()
            return marshal(t.to_dict(), help_desk_fields), 201


