import os
from flask import request
from werkzeug.datastructures import FileStorage
from flask_restful import Resource, reqparse
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import model


class DocumentRawAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('doc', type=FileStorage, location='files', required=True,
                                   help='Doc required')
        super(DocumentRawAPI, self).__init__()

    def post(self, document_id):
        args = self.reqparse.parse_args()

        # Check if the doc exists
        try:
            request.dbs.query(model.Document).filter(model.Document.id == document_id).one()
            doc = args['doc']
            doc.save(app.config['DOCS_URI'] + '/' + document_id + '.pdf')

            return {'success': 'Doc uploaded'}, 201
        except NoResultFound:
            app.logger.warning('Request on non existing document ' + document_id)
            return {}, 404
        except MultipleResultsFound:
            app.logger.error('Multiple results found for document ' + document_id)
            return {}, 500


from app import app