# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
import model
from flask import request
from fields import user_fields
from ws.common.helpers import generate_uuid_for
import hashlib


class UserListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('login', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        self.reqparse.add_argument('role', type=str, location='json')
        self.reqparse.add_argument('last_name', type=str, location='json')
        self.reqparse.add_argument('first_name', type=str, location='json')
        super(UserListAPI, self).__init__()

    def post(self):
        """Creates a new user"""
        args = self.reqparse.parse_args()

        first_name = args.get('first_name', None)
        last_name = args.get('last_name', None)
        role = args.get('role', None)
        #TODO on fait quoi pour le role?

        try:
            login = args['login']
            password = args['password']
        except KeyError:
            return {}, 412

        u = model.User(
            id=generate_uuid_for(request.dbs, model.User),
            login=login,
            password_hash=hashlib.sha1(password).hexdigest(),
            last_name=last_name,
            first_name=first_name,
            role=role
        )
        request.dbs.add(u)
        return marshal(u.to_dict(), user_fields), 201

    def get(self):
        pass
