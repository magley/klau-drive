from .common import *


def add_share_obj(owner: str, username: str, uuid: str, is_album: bool):
    item1 = {
        TB_SHARED_WITH_ME_PK: username,
        TB_SHARED_WITH_ME_SK: uuid,
        TB_SHARED_WITH_ME_FIELD_TYPE: TB_ALBUM_FILES_FIELD_TYPE__FILE if not is_album else TB_ALBUM_FILES_FIELD_TYPE__ALBUM,
        TB_SHARED_WITH_ME_FIELD_OWNER: owner
    }
    item2 = {
        TB_FILE_IS_SHARED_PK: uuid,
        TB_FILE_IS_SHARED_SK: username
    }

    dynamo_cli.put_item(
        TableName=TB_SHARED_WITH_ME_NAME,
        Item=python_obj_to_dynamo_obj(item1)
    )

    dynamo_cli.put_item(
        TableName=TB_FILE_IS_SHARED_NAME,
        Item=python_obj_to_dynamo_obj(item2)
    )


def lambda_share(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']
    username: str = jwt_decode(headers)
    share_single_obj(username, body)
    return http_response("No conent", 204)


def share_single_obj(username: str, body: dict):
    if not user_exists(username):
        return http_response("Forbidden", 401)

    # TODO: If uuid not exists, 404.

    uuid: str = body['uuid']
    username_with_whom_to_share: str = body['username']
    is_album: bool = body['is_album']

    if not has_write_accesss(username, uuid):
        return http_response("You don't own this.", 404)

    if not user_exists(username_with_whom_to_share):
        return http_response("No user with such username", 404)

    if username_with_whom_to_share == username:
        return http_response("Cannot share with yourself!", 400)

    add_share_obj(username, username_with_whom_to_share, uuid, is_album)