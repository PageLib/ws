from flask import request
from flask_restful import Resource, reqparse, marshal
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from fields import doc_fields
import model


class DocumentAPI(Resource):
    def get(self, document_id):
        try:
            doc = request.dbs.query(model.Document).filter(model.Document.id == document_id).one()
            app.logger.info('Successful request on document {}'.format(document_id))
            return marshal(doc.to_dict(), doc_fields)
        except NoResultFound:
            app.logger.warning('Request on non existing document {}'.format(document_id))
            return {}, 404
        except MultipleResultsFound:
            app.logger.error('Multiple results found for document {}'.format(document_id))
            return {}, 500

    def put(self, document_id):
        pass

    def delete(self, document_id):
        pass

from app import app