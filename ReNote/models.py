from marshmallow import Schema, fields
from ReNote import app,db
from flask import jsonify
from bson import ObjectId, json_util
from flask import request
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from mysql.connector import Error as MySQLError
from mysql.connector import errorcode
import mysql.connector


class UserSchema(Schema):
    user_id = fields.Str(required=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    drive_id = fields.Str(required=True)


class DocumentSchema(Schema):
    document_id = fields.Str(required=True, metadata={
                             'unique': True})  # Corrected metadata usage
    name = fields.Str(required=True)
    parent_folder_id = fields.Str()
    created_time = fields.DateTime(required=True)
    modified_time = fields.DateTime(required=True)
    isPin = fields.Bool(required=True)
    isFavourite = fields.Bool(required=True)
    folder_id = fields.Str(required=True)
    tags_id = fields.List(fields.Str(), required=True)
    user_id = fields.Str(required=True)
    drive_id = fields.Str(required=True)
    file_extension = fields.Str(required=True)
    mime_type = fields.Str(required=True)
    


class DriveSchema(Schema):
    drive_id = fields.Str(required=True)
    drive_name = fields.Str(required=True)


class FolderSchema(Schema):
    # Corrected metadata usage
    folder_id = fields.Str(required=True, metadata={'unique': True})
    name = fields.Str(required=True)
    user_id = fields.Str(required=True)
    tags_id = fields.List(fields.Str(), required=True)
    drive_id = fields.Str(required=True)
    created_time = fields.DateTime()
    modified_time = fields.DateTime()


class TagsSchema(Schema):
    tag_id = fields.Str(required=True)
    tag_name = fields.Str(required=True)
    user_id = fields.Str(required=True)
    
AZURE_STORAGE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=necunblobstorage;AccountKey=hgzRK0zpgs+bXf4wnfvFLEJNbSMlbTNeJBuhYHS9jcTrRTzlh0lVlT7K59U8yG0Ojh65p/c4sV97+AStOXtFWw==;EndpointSuffix=core.windows.net'
CONTAINER_NAME = 'pictures'
    
    
    
    
    
    
####################### Data Base CRUD operations ############################
#######  User table Operations #########################
class UserModel:
    @staticmethod
    def create_user(data):
        result = db.user.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_user(user_id):
        data = db.user.find_one({"_id": ObjectId(user_id)})
        return data

    @staticmethod
    def update_user(user_id, updated_data):
        result = db.user.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
        return result.matched_count > 0

    @staticmethod
    def delete_user(user_id):
        result = db.user.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    
############ Document Table Operations ################
class DocumentModel:
    @staticmethod
    def create_document(data):
        result = db.document.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_document(document_id):
        data = db.document.find_one({"_id": ObjectId(document_id)})
        return data

    @staticmethod
    def update_document(document_id, updated_data):
        result = db.document.update_one({"_id": ObjectId(document_id)}, {"$set": updated_data})
        return result.matched_count > 0

    @staticmethod
    def delete_document(document_id):
        result = db.document.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

############# Drive Table Operations ################
class DriveModel:
    @staticmethod
    def create_drive(data):
        result = db.drive.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_drive(drive_id):
        data = db.drive.find_one({"_id": ObjectId(drive_id)})
        return data

    @staticmethod
    def update_drive(drive_id, updated_data):
        result = db.drive.update_one({"_id": ObjectId(drive_id)}, {"$set": updated_data})
        return result.matched_count > 0

    @staticmethod
    def delete_drive(drive_id):
        result = db.drive.delete_one({"_id": ObjectId(drive_id)})
        return result.deleted_count > 0


########### Folder table Operations ################
class FolderModel:
    @staticmethod
    def create_folder(data):
        result = db.folder.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_folder(folder_id):
        data = db.folder.find_one({"_id": ObjectId(folder_id)})
        return data

    @staticmethod
    def update_folder(folder_id, updated_data):
        result = db.folder.update_one({"_id": ObjectId(folder_id)}, {"$set": updated_data})
        return result.matched_count > 0

    @staticmethod
    def delete_folder(folder_id):
        result = db.folder.delete_one({"_id": ObjectId(folder_id)})
        return result.deleted_count > 0

######### Tags Table Operations ################
class TagsModel:
    @staticmethod
    def create_tag(data):
        result = db.tags.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_tag(tag_id):
        data = db.tags.find_one({"_id": ObjectId(tag_id)})
        return data

    @staticmethod
    def update_tag(tag_id, updated_data):
        result = db.tags.update_one({"_id": ObjectId(tag_id)}, {"$set": updated_data})
        return result.matched_count > 0

    @staticmethod
    def delete_tag(tag_id):
        result = db.tags.delete_one({"_id": ObjectId(tag_id)})
        return result.deleted_count > 0
    
class all_methods():
    def upload_image(self,username):
        if 'image' not in request.files:
            return jsonify({'message': 'No image part'}), 400
 
        file = request.files['image']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
   
        filename = secure_filename(file.filename)
        image_url = self.upload_to_azure_blob(file, filename)
       
        response=self.uploading_image_url(username , image_url)
        if response is not None:
            return response
   
       
   
    def upload_to_azure_blob(self,file_stream, file_name):
   
        if not AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("The Azure Storage Connection String is not set or is empty.")
   
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_name)
   
        blob_client.upload_blob(file_stream, overwrite=True)
        return blob_client.url
        
        
    def uploading_image_url(self,username,image_url):
        try:
            db.document.insert_one({"username": username, "image_url": image_url})
            return jsonify({'message': 'Image uploaded successfully', 'url': image_url}), 200
        except Exception as err:
            print("Error:", err)
            return jsonify({'message': 'Failed to upload image'}), 500



document_schema = DocumentSchema()
User_Schema = UserSchema()
Drive_schema = DriveSchema()
folder_schema = FolderSchema()
tags_schema = TagsSchema()
