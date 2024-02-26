from marshmallow import Schema, fields


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


document_schema = DocumentSchema()
User_Schema = UserSchema()
Drive_schema = DriveSchema()
folder_schema = FolderSchema()
tags_schema = TagsSchema()
