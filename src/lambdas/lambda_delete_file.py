from .common import *
import base64


def lambda_delete_file(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    album_uuid: dict = body['album_uuid']
    file_uuid: str = body[CONTENT_METADATA_TB_SK]

    key = {
        CONTENT_METADATA_TB_PK: username,
        CONTENT_METADATA_TB_SK: file_uuid
    }

    dynamo_cli.delete_item(
        Key=python_obj_to_dynamo_obj(key),
        TableName=CONTENT_METADATA_TB_NAME,
    )

    dynamo_cli.delete_item(
        TableName=TB_ALBUM_FILES_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_ALBUM_FILES_PK: album_uuid,
            TB_ALBUM_FILES_SK: file_uuid
        })
    )

    s3_cli.delete_object(
        Bucket=CONTENT_BUCKET_NAME,
        Key=key[CONTENT_METADATA_TB_SK]
    )

    return http_response(None, 204)