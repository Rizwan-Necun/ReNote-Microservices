import json
import logging
from ReNote.models import UserModel, DocumentModel, DriveModel, TagsModel, FolderModel
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


async def convert_document(document):
    document["_id"] = str(document["_id"])
    if "created_time" in document:
        document["created_time"] = document["created_time"].isoformat()
    if "modified_time" in document:
        document["modified_time"] = document["modified_time"].isoformat()
    return document


async def document_to_json(data):
    return json.loads(json_util.dumps(data))



########    User Routes  ########


async def parse_json(data):
    """Convert MongoDB document to JSON."""
    return json.loads(json.dumps(data, default=lambda o: str(o) if isinstance(o, ObjectId) else o))


@app.route('/users', methods=['POST'])
async def create_user():
    data = User_Schema.load(request.get_json())
    user_id = UserModel.create_user(data)
    return jsonify({'message': 'User created successfully', 'id': user_id}), 201

@app.route('/users/<user_id>', methods=['GET'])
async def get_user(user_id):
    user = UserModel.get_user(user_id)
    if user:
        return jsonify(User_Schema.dump(user)), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/users/<user_id>', methods=['PUT'])
async def update_user(user_id):
    user_data = User_Schema.load(request.get_json())
    updated_user = UserModel.update_user(user_id, user_data)
    if updated_user:
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/users/<user_id>', methods=['DELETE'])
async def delete_user(user_id):
    success = UserModel.delete_user(user_id)
    if success:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


############## Folders Routes ################
@app.route('/folders', methods=['POST'])
async def create_folder():
    try:
        # Validate and deserialize input
        data = folder_schema.load(request.get_json())
        folder_id = FolderModel.create_folder(data)
        return jsonify({'message': 'Folder created successfully', 'id': folder_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/folders/<folder_id>', methods=['GET'])
async def get_folder(folder_id):
    folder = FolderModel.get_folder(folder_id)
    if folder:
        # Serialize the output
        return jsonify(folder_schema.dump(folder)), 200
    else:
        return jsonify({'message': 'Folder not found'}), 404

@app.route('/folders/<folder_id>', methods=['PUT'])
async def update_folder(folder_id):
    try:
        folder_data = folder_schema.load(request.get_json())
        if FolderModel.update_folder(folder_id, folder_data):
            return jsonify({'message': 'Folder updated successfully'}), 200
        else:
            return jsonify({'message': 'Folder not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/folders/<folder_id>', methods=['DELETE'])
async def delete_folder(folder_id):
    if FolderModel.delete_folder(folder_id):
        return jsonify({'message': 'Folder deleted successfully'}), 200
    else:
        return jsonify({'message': 'Folder not found'}), 404

########### Document  Routes ###########

@app.route('/documents', methods=['POST'])
async def create_document():
    data = document_schema.load(request.get_json())
    document_id = DocumentModel.create_document(data)
    return jsonify({'message': 'Document created successfully', 'id': document_id}), 201

@app.route('/documents/<document_id>', methods=['GET'])
async def get_document(document_id):
    document = DocumentModel.get_document(document_id)
    if document:
        return jsonify(document_schema.dump(document)), 200
    else:
        return jsonify({'message': 'Document not found'}), 404

@app.route('/documents/<document_id>', methods=['PUT'])
async def update_document(document_id):
    document_data = document_schema.load(request.get_json())
    updated_document = DocumentModel.update_document(document_id, document_data)
    if updated_document:
        return jsonify({'message': 'Document updated successfully'}), 200
    else:
        return jsonify({'message': 'Document not found'}), 404

@app.route('/documents/<document_id>', methods=['DELETE'])
async def delete_document(document_id):
    success = DocumentModel.delete_document(document_id)
    if success:
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'message': 'Document not found'}), 404


####### Tags Routes ########

@app.route('/tags', methods=['POST'])
async def create_tag():
    try:
        # Validate and deserialize input
        data = tags_schema.load(request.get_json())
        tag_id = TagsModel.create_tag(data)
        return jsonify({'message': 'Tag created successfully', 'id': tag_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/tags/<tag_id>', methods=['GET'])
async def get_tag(tag_id):
    tag = TagsModel.get_tag(tag_id)
    if tag:
        # Serialize the output
        return jsonify(tags_schema.dump(tag)), 200
    else:
        return jsonify({'message': 'Tag not found'}), 404

@app.route('/tags/<tag_id>', methods=['PUT'])
async def update_tag(tag_id):
    try:
        tag_data = tags_schema.load(request.get_json())
        if TagsModel.update_tag(tag_id, tag_data):
            return jsonify({'message': 'Tag updated successfully'}), 200
        else:
            return jsonify({'message': 'Tag not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/tags/<tag_id>', methods=['DELETE'])
async def delete_tag(tag_id):
    if TagsModel.delete_tag(tag_id):
        return jsonify({'message': 'Tag deleted successfully'}), 200
    else:
        return jsonify({'message': 'Tag not found'}), 404


##### Drive Routes #####
@app.route('/drives', methods=['POST'])
async def create_drive():
    try:
        # Validate and deserialize input
        data = Drive_schema.load(request.get_json())
        drive_id = DriveModel.create_drive(data)
        return jsonify({'message': 'Drive created successfully', 'id': drive_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/drives/<drive_id>', methods=['GET'])
async def get_drive(drive_id):
    drive = DriveModel.get_drive(drive_id)
    if drive:
        # Serialize the output
        return jsonify(Drive_schema.dump(drive)), 200
    else:
        return jsonify({'message': 'Drive not found'}), 404

@app.route('/drives/<drive_id>', methods=['PUT'])
async def update_drive(drive_id):
    try:
        drive_data = Drive_schema.load(request.get_json())
        if DriveModel.update_drive(drive_id, drive_data):
            return jsonify({'message': 'Drive updated successfully'}), 200
        else:
            return jsonify({'message': 'Drive not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/drives/<drive_id>', methods=['DELETE'])
async def delete_drive(drive_id):
    if DriveModel.delete_drive(drive_id):
        return jsonify({'message': 'Drive deleted successfully'}), 200
    else:
        return jsonify({'message': 'Drive not found'}), 404


    
    
    
    
    
    
    
    
# @app.route('/upload_image', methods=['POST'])
# @token_required
# def upload_image_main(self,redis_user,token_user, token_email, token_application_id, token_client_id, token):
   
#     # method_response=all_methods_instance.upload_image(token_user)
#     # if method_response is not None:
#     #     return method_response
    
#     def upload_image(self,username):
#         if 'image' not in request.files:
#             return jsonify({'message': 'No image part'}), 400
 
#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'message': 'No selected file'}), 400
   
#         filename = secure_filename(file.filename)
#         image_url = self.upload_to_azure_blob(file, filename)
       
#         response=db_instance.uploading_image_url(username , image_url)
#         if response is not None:
#             return response
   
       
   
#     def upload_to_azure_blob(self,file_stream, file_name):
   
#         if not AZURE_STORAGE_CONNECTION_STRING:
#             raise ValueError("The Azure Storage Connection String is not set or is empty.")
   
#         blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#         blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_name)
   
#         blob_client.upload_blob(file_stream, overwrite=True)
