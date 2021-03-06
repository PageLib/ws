from flask_restful import Resource, reqparse, marshal
from flask import request
import model
from ws.common.helpers import generate_uuid_for
from ws.iam.fields import entity_fields
from sqlalchemy import not_
from ws.common.helpers import get_or_412


class EntityListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location=('json', 'values'))
        super(EntityListAPI, self).__init__()

    def get(self):
        """
        Search for entity by name.
        """
        query = request.dbs.query(model.Entity).filter(not_(model.Entity.deleted))

        #optional filters
        args = self.reqparse.parse_args()
        if args.get('name', None):
            name_search = '%' + args['name'] + '%'
            query = query.filter(model.Entity.name.like(name_search))

        return {'entities': map(lambda e: marshal(e.to_dict(), entity_fields), query.all())}

    def post(self):
        """
        Creates a new entity.
        """
        args = self.reqparse.parse_args()
        name = get_or_412(args, 'name')

        # Check if the another entity has the same name.
        q = request.dbs.query(model.Entity).filter(not_(model.Entity.deleted))\
                                           .filter(model.Entity.name == name)

        if request.dbs.query(q.exists()).scalar():
            app.logger.warning('Tried to create an entity with already existing name')
            return {'error': 'Entity with the same name already exists.'}, 412
        id = generate_uuid_for(request.dbs, model.Entity)
        e = model.Entity(
            id=id,
            name=name,
            deleted=False
        )
        request.dbs.add(e)
        app.logger.info('Entity {} (uuid: {} ) created'.format(name, id))
        return marshal(e.to_dict(), entity_fields)


from app import app