# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
import model
from model import User
from flask import request
from fields import user_fields
from ws.common.helpers import generate_uuid_for
import hashlib
from roles import roles
from sqlalchemy import and_, not_, exists


class UserListAPI(Resource):

    def post(self):
        """Creates a new user"""
        # Parse the arguments.
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, location='json', required=True, help='Missing login')
        parser.add_argument('password', type=str, location='json', required=True, help='Missing password')
        parser.add_argument('role', type=str, location='json', required=True, help='Missing role')
        parser.add_argument('entity_id', type=str, location='json', required=True, help='Missing entity_id.')
        parser.add_argument('last_name', type=str, location='json')
        parser.add_argument('first_name', type=str, location='json')
        args = parser.parse_args()

        first_name = args.get('first_name', None)
        last_name = args.get('last_name', None)
        role = args['role']
        entity_id = args['entity_id']
        login = args['login']
        password = args['password']
        
        #Check if the role is correct
        if role not in roles:
            app.logger.warning('Request on POST UserListAPI for non existing or missing role')
            return {'error': 'Role POSTed is not allowed'}, 412

        # We check if another non deleted user has the same login
        user_same_login_exists = request.dbs.query(exists().where(and_(User.login == login,
                                                                       not_(User.deleted)))).scalar()
        if user_same_login_exists:
            return {'error': 'User with the same login exists.'}, 412

        # Check if the entity exists
        if not request.dbs.query(exists().where(and_(model.Entity.id == entity_id,
                                                     not_(model.Entity.deleted)))).scalar():
            app.logger.warning('Request on POST UserListAPI with entity_id {} not found'.format(entity_id))
            return {'error': 'entity_id doesn\'t exists'}, 412

        # Write the user in DB.
        user_id = generate_uuid_for(request.dbs, User)
        u = User(
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
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, location='values')
        parser.add_argument('first_name', type=str, location='values')
        parser.add_argument('last_name', type=str, location='values')
        args = parser.parse_args()
        
        query = request.dbs.query(User)
        
        # Optional filters
        if args.get('login', None):
            query = query.filter(User.login == args['login'])

        if args.get('first_name', None):
            name_search = '%' + args['first_name'] + '%'
            query = query.filter(User.first_name.like(name_search))

        if args.get('last_name', None):
            name_search = '%' + args['last_name'] + '%'
            query = query.filter(User.first_name.like(name_search))

        return {'users': map(lambda u: marshal(u.to_dict(), user_fields), query.all())}


from app import app