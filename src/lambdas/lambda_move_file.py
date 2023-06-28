from .common import *


def get_album_entry(album_uuid: str, uuid: str):
    statement = f"""
        SELECT * FROM {TB_ALBUM_FILES_NAME}
        WHERE
            {TB_ALBUM_FILES_PK}=? AND
            {TB_ALBUM_FILES_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([album_uuid, uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        return obj # There should be only 1.
    return {}


def lambda_move_file(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    uuid: str = body['uuid']
    album_old_uuid: str = body['album_old_uuid']
    album_new_uuid: str = body['album_new_uuid']
    cut: bool = body['cut']

    if not has_write_accesss(username, uuid):
        return http_response("You don't own this.", 404)
    
    if filename_used(uuid, get_file_name(username, uuid), username, album_new_uuid):
        return http_response("Can't update, filename in use!", 400)

    if album_old_uuid == album_new_uuid:
        return http_response(None, 204)
    
    if album_new_uuid == uuid:
        return http_response("Can't move album into itself!", 400)

    key_old = {
        TB_ALBUM_FILES_PK: album_old_uuid,
        TB_ALBUM_FILES_SK: uuid
    }

    item = get_album_entry(album_old_uuid, uuid)
    item[TB_ALBUM_FILES_PK] = album_new_uuid

    if cut:
        dynamo_cli.delete_item(
            TableName=TB_ALBUM_FILES_NAME,
            Key=python_obj_to_dynamo_obj(key_old),
        )

    dynamo_cli.put_item(
        TableName=TB_ALBUM_FILES_NAME,
        Item=python_obj_to_dynamo_obj(item)
    )

    send_email(username, f"You have just moved a file: {uuid}", "File moved")
    return http_response(None, 204)
