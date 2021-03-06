# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
import model
from flask import request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from fields import user_fields
from roles import roles
from sqlalchemy import not_
from ws.iam.internal_helpers import ensure_allowed


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('login', type=str, location='json')
        self.reqparse.add_argument('password_hash', type=str, location='json')
        self.reqparse.add_argument('role', type=str, location='json')
        self.reqparse.add_argument('first_name', type=str, location='json')
        self.reqparse.add_argument('entity_id', type=str, location='json')
        self.reqparse.add_argument('last_name', type=str, location='json')
        super(UserAPI, self).__init__()

    def get(self, user_id):
        """
        GET the user with the good user_id.
        """
        # Check permission
        resource = 'own_user' if user_id == request.ws_session.user_id else 'user'
        ensure_allowed('read', resource)
        try:
            user = request.dbs.query(model.User).join(model.Entity)\
                                                .filter(model.User.id == user_id)\
                                                .filter(not_(model.User.deleted))\
                                                .filter(not_(model.Entity.deleted)).one()

            app.logger.info('Successful request on user {}'.format(user_id))
            return marshal(user.to_dict(), user_fields)

        except NoResultFound:
            app.logger.warning('Request on non existing user {}'.format(user_id))
            return {}, 404

        except MultipleResultsFound:
            app.logger.error('Multiple results found for user {}'.format(user_id))
            return {}, 500

    def put(self, user_id):
        """
        Updates a user.
        """
        # Check permission
        resource = 'own_user' if user_id == request.ws_session.user_id else 'user'
        ensure_allowed('update', resource)
        try:
            user = request.dbs.query(model.User).join(model.Entity)\
                                                .filter(model.User.id == user_id)\
                                                .filter(not_(model.User.deleted))\
                                                .filter(not_(model.Entity.deleted)).one()

            app.logger.info('Request on user {}'.format(user_id))

        except NoResultFound:
            app.logger.warning('PUT Request on non existing user {}'.format(user_id))
            return {}, 404

        except MultipleResultsFound:
            app.logger.error('Multiple results found for user {} on PUT UserAPI'.format(user_id))
            return {}, 500

        args = self.reqparse.parse_args()
        if args['login'] is not None:
            # We check if another non deleted user has the same login
            login = args['login']
            q = request.dbs.query(model.User).join(model.Entity)\
                                             .filter(not_(model.User.deleted))\
                                             .filter(not_(model.Entity.deleted))\
                                             .filter(model.User.login == login)

            if request.dbs.query(q.exists()).scalar():
                app.logger.warning('Tried to create an user with already existing name')
                return {'error': 'User with the same login exists.'}, 412

            user.login = login
        if args['entity_id'] is not None:
            user.entity_id = args['entity_id']
        if args['password_hash'] is not None:
            user.password_hash = args['password_hash']
        if args['role'] is not None:
            role = args['role']
            if role in roles:
                user.role = role
            else:
                return {'error': 'Role \'' + role + '\' is not allowed'}, 412
        if args['first_name'] is not None:
            user.first_name = args['first_name']
        if args['last_name'] is not None:
            user.last_name = args['last_name']
        app.logger.info('User {} successfully updated'.format(user_id))
        return marshal(user.to_dict(), user_fields)

    def delete(self, user_id):
        """
        Deletes a user.
        """
        # Check permission
        resource = 'own_user' if user_id == request.ws_session.user_id else 'user'
        ensure_allowed('delete', resource)

        try:
            user = request.dbs.query(model.User).join(model.Entity)\
                                                .filter(model.User.id == user_id)\
                                                .filter(not_(model.User.deleted))\
                                                .filter(not_(model.Entity.deleted)).one()

            user.deleted = True
            app.logger.info('User {} deleted'.format(user_id))
            return {'user_deleted': True}, 200

        except NoResultFound:
            app.logger.warning('DELETE Request on non existing user {}'.format(user_id))
            return 404

        except MultipleResultsFound:
            app.logger.error('Multiple results found for user {} on DELETE UserAPI'.format(user_id))
            return 500


from app import app