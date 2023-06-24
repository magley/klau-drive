from .common import *


def add_share_obj(owner: str, username: str, uuid: str, is_album: bool):
    item1 = {
        TB_SHARE_PK: owner,
        TB_SHARE_SK: uuid,
        TB_SHARE_FIELD_TYPE: TB_ALBUM_FILES_FIELD_TYPE__FILE if not is_album else TB_ALBUM_FILES_FIELD_TYPE__ALBUM,
        TB_SHARE_FIELD_USER: username
    }

    dynamo_cli.put_item(    
        TableName=TB_SHARE_NAME,
        Item=python_obj_to_dynamo_obj(item1)
    )


def lambda_share(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    # Is username_with_whom_to_share not exists, 404.
    # If uuid not exists, 404.
 
    uuid: str = body['uuid']
    username_with_whom_to_share: str = body['username']
    is_album: bool = body['is_album']

    add_share_obj(username, username_with_whom_to_share, uuid, is_album)

    return http_response("No conent", 204)
