import datetime
import os
from flask import request
from flask_restful import Resource, reqparse, marshal
import model
from fields import doc_fields
from ws.common.helpers import generate_uuid_for


class DocumentListAPI(Resource):

    def get(self):
        pass

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json', required=True,
                            help='name required')
        parser.add_argument('user_id', type=str, location='json', required=True,
                            help='user_id required')

        args = parser.parse_args()

        name = args['name']
        user_id = args['user_id']

        # TODO Check if the user exists

        id = generate_uuid_for(request.dbs, model.Document)
        d = model.Document(
            id=id,
            user_id=user_id,
            name=name,
            date_time=datetime.datetime.now()
        )
        request.dbs.add(d)
        app.logger.info('{} uploaded raw file {}'.format(id, user_id))
        return marshal(d.to_dict(), doc_fields)

from app import app
