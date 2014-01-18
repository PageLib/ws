from flask_restful import Resource, reqparse, marshal
from flask import request
import model
from ws.common.helpers import generate_uuid_for
from ws.iam.fields import entity_fields


class EntityListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        super(EntityListAPI, self).__init__()

    def post(self):
        """
        Creates a new entity.
        """
        args = self.reqparse.parse_args()
        try:
            name = args['name']
        except KeyError:
            app.logger.info('Request on POST EntityListAPI without name in JSON')
            return {}, 412
        print 'plop'
        id = generate_uuid_for(request.dbs)
        e = model.Entity(
            id=id,
            name=name
        )
        request.dbs.add(e)
        app.logger.info('Entity {} (uuid: {} ) created'.format(name, id))
        return marshal(e.to_dict(), entity_fields)


from app import app