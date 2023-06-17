
from .common import *


def album_uuid_to_album_metadata(username: str, album_uuid: str) -> dict:
    statement = f"""
        SELECT * FROM {TB_USER_ALBUMS_NAME}
        WHERE
            {TB_USER_ALBUMS_PK}=? AND
            {TB_USER_ALBUMS_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, album_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        return obj # There should be only 1.
    return {}


def file_uuid_to_file_metadata(username: str, file_uuid: str) -> dict:
    statement = f"""
        SELECT * FROM {CONTENT_METADATA_TB_NAME}
        WHERE
            {CONTENT_METADATA_TB_PK}=? AND
            {CONTENT_METADATA_TB_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, file_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        return obj # There should be only 1.
    return {}    


def lambda_list_files(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']
    album_uuid: str = body['album_uuid']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    items = get_album_files(album_uuid)

    result = []
    for o in items:
        album_item = dynamo_obj_to_python_obj(o)
        item_uuid = album_item[TB_ALBUM_FILES_SK]
        item_type = album_item[TB_ALBUM_FILES_FIELD_TYPE]

        item = {
            "uuid": item_uuid,
            "type": item_type,
            "content": {}
        }

        if item_type == TB_ALBUM_FILES_FIELD_TYPE__ALBUM:
            item['content'] = album_uuid_to_album_metadata(username, item_uuid)
        else:
            item['content'] = file_uuid_to_file_metadata(username, item_uuid)

        result.append(item)

    return http_response(result, 200)