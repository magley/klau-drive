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

    dynamo_cli.put_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Item=metadata_dynamojson
    )

    s3_cli.upload_fileobj(
        Fileobj=io.BytesIO(data),
        Bucket=CONTENT_BUCKET_NAME,
        Key=metadata[CONTENT_METADATA_TB_SK]
    )

    return http_response(None, 204)