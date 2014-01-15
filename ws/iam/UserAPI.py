# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
import model
from flask import request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from fields import user_fields
from ws.common.helpers import generate_uuid_for
import hashlib

class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('login', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        self.reqparse.add_argument('role', type=str, location='json')
        self.reqparse.add_argument('first_name', type=str, location='json')
        self.reqparse.add_argument('last_name', type=str, location='json')
        super(UserAPI, self).__init__()

    def get(self, user_id):
        try:
            user = request.dbs.query(model.User).filter(model.User.id == user_id).one()
        except NoResultFound:
            return 404

        except MultipleResultsFound:
            # TODO: log something
            return 500
        return marshal(user.to_dict(), user_fields)

    def put(self):
        pass

