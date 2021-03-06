from flask_restful import Resource, reqparse, marshal
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import request
import model
from ws.iam.fields import entity_fields
from sqlalchemy import not_


class EntityAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        super(EntityAPI, self).__init__()

    def get(self, entity_id):
        """
        Return an entity.
        """
        try:
            entity = request.dbs.query(model.Entity).filter(model.Entity.id == entity_id)\
                                                    .filter(not_(model.Entity.deleted)).one()
        except NoResultFound:
            app.logger.warning('GET Request on non existing entity {}'.format(entity_id))
            return {}, 404

        except MultipleResultsFound:
            app.logger.error('Multiple results found for entity {} on GET EntityAPI'.format(entity_id))
            return {}, 500

        return marshal(entity.to_dict(), entity_fields)

    def put(self, entity_id):
        """
        Updates an entity.
        """
        try:
            entity = request.dbs.query(model.Entity).filter(model.Entity.id == entity_id)\
                                                    .filter(not_(model.Entity.deleted)).one()
        except NoResultFound:
            app.logger.warning('PUT Request on non existing entity {}'.format(entity_id))
            return {}, 404

        except MultipleResultsFound:
            app.logger.error('Multiple results found for entity {} on PUT EntityAPI'.format(entity_id))
            return {}, 500

        args = self.reqparse.parse_args()
        name = args.get('name', None)
        if name is not None:
            entity.name = name

        app.logger.info('Entity {} updated'.format(entity_id))
        return marshal(entity.to_dict(), entity_fields)

    def delete(self, entity_id):
        """
        Soft-delete the entity called.
        """
        try:
            entity = request.dbs.query(model.Entity).filter(model.Entity.id == entity_id)\
                                                    .filter(not_(model.Entity.deleted)).one()
        except NoResultFound:
            app.logger.warning('DELETE Request on non existing entity {}'.format(entity_id))
            return {}, 404

        except MultipleResultsFound:
            app.logger.error('Multiple results found for entity {} on DELETE EntityAPI'.format(entity_id))
            return {}, 500
        entity.deleted = True
        return {'entity_deleted': True}, 200

from app import app