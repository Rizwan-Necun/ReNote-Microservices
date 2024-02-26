import json
import logging

import pymongo
from bson import ObjectId, json_util
from flask import Flask, jsonify, request
from marshmallow import Schema, ValidationError, fields
from ReNote import app, db
from ReNote.models import (Drive_schema, User_Schema,
                           document_schema, tags_schema, folder_schema)
from azure.storage.blob import BlobServiceClient



AZURE_STORAGE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=necunblobstorage;AccountKey=hgzRK0zpgs+bXf4wnfvFLEJNbSMlbTNeJBuhYHS9jcTrRTzlh0lVlT7K59U8yG0Ojh65p/c4sV97+AStOXtFWw==;EndpointSuffix=core.windows.net'
CONTAINER_NAME = 'pictures'

############# HELPERS #########


def convert_document(document):
    document["_id"] = str(document["_id"])
    if "created_time" in document:
        document["created_time"] = document["created_time"].isoformat()
    if "modified_time" in document:
        document["modified_time"] = document["modified_time"].isoformat()
    return document


def document_to_json(data):
    return json.loads(json_util.dumps(data))



########    User Routes  ########


@app.route('/user', methods=['POST'])
async def create_user():
    try:
        data = User_Schema.load(request.get_json())
        result = db.user.insert_one(data)
        return jsonify({'message': 'user created successfully', 'id': str(result.inserted_id)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400


@app.route('/user/<user_id>', methods=['GET'])
async def get_user(user_id):
    try:
        data = db.user.find_one({"_id": ObjectId(user_id)})
        if data is not None:
            return jsonify(json.loads(json.dumps(data, default=str))), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/user/<user_id>', methods=['PUT'])
async def update_user(user_id):
    try:
        updated_data = User_Schema.load(request.get_json())
        db.user.update_one({"_id": ObjectId(user_id)}, {
            "$set": updated_data})
        return jsonify({'message': 'user updated successfully'}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/user/<user_id>', methods=['DELETE'])
async def delete_user(user_id):
    try:
        result = db.user.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count:
            return jsonify({'message': 'user deleted successfully'}), 200
        else:
            return jsonify({'message': 'user not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


############## Folders Routes ################
@app.route('/folder', methods=['POST'])
async def create_folder():
    try:
        data = folder_schema.load(request.get_json())
        result = db.folders.insert_one(data).inserted_id
        return jsonify({'message': 'Folder created successfully', 'id': str(result)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400


@app.route('/folder/<folder_id>', methods=['GET'])
async def get_folder(folder_id):
    try:
        data = db.folders.find_one({"_id": ObjectId(folder_id)})
        if data is not None:
            # Convert the MongoDB document to the desired format
            converted_data = convert_document(data)
            return jsonify(converted_data), 200
        else:
            return jsonify({'message': 'Folder not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/folder/<folder_id>', methods=['PUT'])
async def update_folder(folder_id):
    try:
        updated_data = folder_schema.load(request.get_json())
        result = db.folders.update_one(
            {"_id": ObjectId(folder_id)}, {"$set": updated_data})
        if result.matched_count:
            return jsonify({'message': 'Folder updated successfully'}), 200
        else:
            return jsonify({'message': 'Folder not found'}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400


@app.route('/folder/<folder_id>', methods=['DELETE'])
async def delete_folder(folder_id):
    try:
        result = db.folders.delete_one({"_id": ObjectId(folder_id)})
        if result.deleted_count:
            return jsonify({'message': 'Folder deleted successfully'}), 200
        else:
            return jsonify({'message': 'Folder not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

########### Document  Routes ###########


@app.route('/document', methods=['POST'])
async def create_document():
    try:
        data = document_schema.load(request.get_json())
        result = db.documents.insert_one(data)
        return jsonify({'message': 'Document created successfully', 'id': str(result.inserted_id)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400


@app.route('/document/<document_id>', methods=['GET'])
async def get_document(document_id):
    try:
        data = db.documents.find_one({"_id": ObjectId(document_id)})
        if data is not None:
            return jsonify(json.loads(json.dumps(data, default=str))), 200
        else:
            return jsonify({'message': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/document/<document_id>', methods=['PUT'])
async def update_document(document_id):
    try:
        updated_data = document_schema.load(request.get_json())
        db.documents.update_one({"_id": ObjectId(document_id)}, {
                                "$set": updated_data})
        return jsonify({'message': 'Document updated successfully'}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/document/<document_id>', methods=['DELETE'])
async def delete_document(document_id):
    try:
        result = db.documents.delete_one({"_id": ObjectId(document_id)})
        if result.deleted_count:
            return jsonify({'message': 'Document deleted successfully'}), 200
        else:
            return jsonify({'message': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

####### Tags Routes ########


@app.route('/tags', methods=['POST'])
async def create_tags():
    try:
        data = tags_schema.load(request.get_json())
        result = db.Tags.insert_one(data)
        return jsonify({'message': 'Tags created successfully', 'id': str(result.inserted_id)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/tags/<tags_id>', methods=['GET'])
async def get_tags(tags_id):
    try:
        data = db.Tags.find_one({"_id": ObjectId(tags_id)})
        if data is not None:
            # Convert _id from ObjectId to string
            data['_id'] = str(data['_id'])
            return jsonify(data), 200
        else:
            return jsonify({'message': 'Tags not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/tags/<tags_id>', methods=['PUT'])
async def update_tags(tags_id):
    try:
        updated_data = tags_schema.load(request.get_json())
        result = db.Tags.update_one(
            {"_id": ObjectId(tags_id)}, {"$set": updated_data})
        if result.matched_count:
            return jsonify({'message': 'Tags updated successfully'}), 200
        return jsonify({'message': 'Tags not found'}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/tags/<tags_id>', methods=['DELETE'])
async def delete_tags(tags_id):
    try:
        result = db.Tags.delete_one({"_id": ObjectId(tags_id)})
        if result.deleted_count:
            return jsonify({'message': 'Tags deleted successfully'}), 200
        return jsonify({'message': 'Tags not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


##### Drive Routes #####
@app.route('/drive', methods=['POST'])
async def create_drive():
    try:
        data = Drive_schema.load(request.get_json())
        result = db.Drive.insert_one(data)
        return jsonify({'message': 'Drive created successfully', 'id': str(result.inserted_id)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/drive/<drive_id>', methods=['GET'])
async def drive_tags(drive_id):
    try:
        data = db.Drive.find_one({"_id": ObjectId(drive_id)})
        if data is not None:
            # Convert _id from ObjectId to string
            data['_id'] = str(data['_id'])
            return jsonify(data), 200
        else:
            return jsonify({'message': 'Drive not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/drive/<drive_id>', methods=['PUT'])
async def update_drive(drive_id):
    try:
        updated_data = Drive_schema.load(request.get_json())
        result = db.Drive.update_one(
            {"_id": ObjectId(drive_id)}, {"$set": updated_data})
        if result.matched_count:
            return jsonify({'message': 'Drive updated successfully'}), 200
        return jsonify({'message': 'Drive not found'}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/drive/<drive_id>', methods=['DELETE'])
async def delete_drive(drive_id):
    try:
        result = db.Drive.delete_one({"_id": ObjectId(drive_id)})
        if result.deleted_count:
            return jsonify({'message': 'Drive deleted successfully'}), 200
        return jsonify({'message': 'Tags not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
