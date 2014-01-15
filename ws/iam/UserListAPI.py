# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
import model
from flask import request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from fields import user_fields
from ws.common.helpers import generate_uuid_for
import hashlib

class UserListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('login', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        self.reqparse.add_argument('last_name', type=str, location='json')
        self.reqparse.add_argument('first_name', type=str, location='json')
        super(UserListAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        try:
            login = args['login']
            password = args['password']
        except KeyError:
            return 412

        first_name = args.get('first_name', None)
        last_name = args.get('last_name', None)

        u = model.User(
            id=generate_uuid_for(request.dbs, model.User),
            login=login,
            password_hash=hashlib.sha1(password).hexdigest(),
            last_name=last_name,
            first_name=first_name
        )
        request.dbs.add(u)