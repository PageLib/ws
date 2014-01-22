# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
import model
from flask import request
from fields import user_fields
from ws.common.helpers import generate_uuid_for
import hashlib
from roles import check_role
from sqlalchemy import exists
from sqlalchemy import and_, not_


class UserListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('login', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        self.reqparse.add_argument('role', type=str, location='json')
        self.reqparse.add_argument('last_name', type=str, location='json')
        self.reqparse.add_argument('first_name', type=str, location='json')
        self.reqparse.add_argument('entity_id', type=str, location='json')
        super(UserListAPI, self).__init__()

    def post(self):
        """Creates a new user"""
        args = self.reqparse.parse_args()

        first_name = args.get('first_name', None)
        last_name = args.get('last_name', None)
        role = args.get('role', None)
        if not check_role(role):
            app.logger.warning('Request on POST UserListAPI for non existing role {}'.format(role))
            return {'error': 'Role \'' + role + '\' is not allowed'}, 412

        login = args['login']
        password = args['password']
        entity_id = args['entity_id']
        if not (login and password and entity_id):
            app.logger.warning('Request on POST UserListAPI with missing login, entity_id or password in json')
            return {}, 412

        # We check if another non deleted user has the same login
        user_same_login_exists = request.dbs.query(exists().where(and_(model.User.login == login,
                                                                   not_(model.User.deleted)))).scalar()
        if user_same_login_exists:
            return {'error': 'User with the same login exists.'}, 412

        # Check that the entity exists
        if not request.dbs.query(exists().where(model.Entity.id == entity_id)
                                         .where(not_(model.Entity.deleted))).scalar():
            app.logger.warning('Request on POST UserListAPI with unknown or deleted entity_id : ' + entity_id)
            return {'error': 'Unknown entity_id : {}'.format(entity_id)}

        user_id = generate_uuid_for(request.dbs, model.User)
        u = model.User(
            id=user_id,
            login=login,
            password_hash=hashlib.sha1(password).hexdigest(),
            last_name=last_name,
            first_name=first_name,
            role=role,
            deleted=False,
            entity_id=entity_id
        )
        request.dbs.add(u)
        app.logger.info('User {} (uuid: {}) created'.format(login, user_id))
        return marshal(u.to_dict(), user_fields), 201

    def get(self):
        pass

from app import app