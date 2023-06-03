from typing import Dict
from .common import *
import base64

def base64url_decode(input):
    return base64.urlsafe_b64decode(input + '==')


def manage_token(auth_header: str) -> str:
    parts = auth_header.split()
    jwt = parts[1]

    jwt_body_str: str = jwt.split('.')[1]
    jwt_body: Dict = json.loads(base64url_decode(jwt_body_str))
    username = jwt_body['username']

    return username


def lambda_delete_file(event: Dict, context):
    body: Dict = json.loads(event['body'])
    headers: Dict = event['headers']
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

    return http_response(manage_token(headers['Authorization']), 200)