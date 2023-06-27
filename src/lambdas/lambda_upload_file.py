import base64
import io

from .common import *


def lambda_upload_file(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
     
    metadata: dict = body['metadata']
    metadata_dynamojson: str = python_obj_to_dynamo_obj(metadata)
    data: bytes = base64.b64decode(body['data'])
    album_uuid: str = body['album_uuid']

    if not has_write_accesss(username, album_uuid):
        return http_response("You don't own this.", 404)

    tb_album_files_record: dict = python_obj_to_dynamo_obj({
        TB_ALBUM_FILES_PK: album_uuid,
        TB_ALBUM_FILES_SK: metadata['uuid'],
        TB_ALBUM_FILES_FIELD_TYPE: TB_ALBUM_FILES_FIELD_TYPE__FILE,
    })

    dynamo_cli.put_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Item=metadata_dynamojson
    )

    dynamo_cli.put_item(
        TableName=TB_ALBUM_FILES_NAME,
        Item=tb_album_files_record
    )

    success = False

    try:
        #raise Exception()
        s3_cli.upload_fileobj(
            Fileobj=io.BytesIO(data),
            Bucket=CONTENT_BUCKET_NAME,
            Key=metadata[CONTENT_METADATA_TB_SK]
        )
        success = True
    except Exception as e:
        dynamo_cli.delete_item(
            TableName=CONTENT_METADATA_TB_NAME,
            Key=python_obj_to_dynamo_obj({
                CONTENT_METADATA_TB_PK: username,
                CONTENT_METADATA_TB_SK: metadata['uuid']
            })
        )
        dynamo_cli.delete_item(
            TableName=TB_ALBUM_FILES_NAME,
            Key=python_obj_to_dynamo_obj({
                TB_ALBUM_FILES_PK: album_uuid,
                TB_ALBUM_FILES_SK: metadata['uuid']
            })
        )
        success = False

    if not success:
        return http_response("Failed to upload, fixing consistency.", 500)
    else:
        return http_response("", 204)