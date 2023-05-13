import base64
import io
from typing import Dict
from common import *


# TODO: Create a lambda that initializes the dynamodb table and s3 bucket.
def create_bucket_if_not_exists(bucket_name):
    s3_cli.create_bucket(Bucket=bucket_name)


def lambda_upload_file(event: Dict, context):
    body: Dict = json.loads(event['body'])
    metadata: Dict = body['metadata']
    metadata_dynamojson: str = python_obj_to_dynamo_obj(metadata)
    data: bytes = base64.b64decode(body['data'])

    create_bucket_if_not_exists(CONTENT_BUCKET_NAME)
    create_table_if_not_exists(CONTENT_METADATA_TB_NAME, CONTENT_METADATA_TB_PK, CONTENT_METADATA_TB_SK)

    dynamo_cli.put_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Item=metadata_dynamojson
    )

    s3_cli.upload_fileobj(
        Fileobj=io.BytesIO(data),
        Bucket=CONTENT_BUCKET_NAME,
        Key=metadata['name']
    )

    return http_response(None, 204)