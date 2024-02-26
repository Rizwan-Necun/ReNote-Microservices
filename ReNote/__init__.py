import json
import logging

import pymongo
from bson import ObjectId
from flask import Flask, jsonify, request
from marshmallow import Schema, ValidationError, fields


app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
try:
    mongo = pymongo.MongoClient(
        host='localhost', port=27017, serverSelectionTimeoutMS=1000)
    db = mongo.RenoteMicroservice1
    mongo.server_info()
    logging.info('Connected to MongoDB')
except pymongo.errors.ServerSelectionTimeoutError as e:
    logging.error(f'Error connecting to MongoDB: {e}')

##################
from ReNote import routes
# from models import (Drive_schema, User_Schema, document_schema, folder_schema,
#                     tags_schema)
###################
