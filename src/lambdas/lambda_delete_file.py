from typing import Dict
from .common import *


def lambda_delete_file(event: Dict, context):
    body: Dict = json.loads(event['body'])
    key = {
        CONTENT_METADATA_TB_PK: body['username'],
        CONTENT_METADATA_TB_SK: body['uuid']
    }

    dynamo_cli.delete_item(
        Key=python_obj_to_dynamo_obj(key),
        TableName=CONTENT_METADATA_TB_NAME,
    )

    s3_cli.delete_object(
        Bucket=CONTENT_BUCKET_NAME,
        Key=key['uuid']
    )
    
    return http_response(None, 204)