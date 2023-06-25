from .common import *


def lambda_album_add(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    parent_uuid: str = body['parent_uuid']
    uuid: str = body['uuid']
    name: str = body['name']

    if not has_write_accesss(username, parent_uuid):
        return http_response("You don't own this.", 404)

    tb_user_albums_entry = {
        TB_USER_ALBUMS_PK: username,
        TB_USER_ALBUMS_SK: uuid,
        TB_USER_ALBUMS_FIELD_NAME: name
    }

    tb_album_files_entry = {
        TB_ALBUM_FILES_PK: parent_uuid,
        TB_ALBUM_FILES_SK: uuid,
        TB_ALBUM_FILES_FIELD_TYPE: TB_ALBUM_FILES_FIELD_TYPE__ALBUM
    }

    dynamo_cli.put_item(
        TableName=TB_USER_ALBUMS_NAME,
        Item=python_obj_to_dynamo_obj(tb_user_albums_entry)
    )
    dynamo_cli.put_item(
        TableName=TB_ALBUM_FILES_NAME,
        Item=python_obj_to_dynamo_obj(tb_album_files_entry)
    )

    return http_response(None, 204)