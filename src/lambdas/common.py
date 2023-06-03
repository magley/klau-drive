from typing import Dict
import base64
import json
import boto3
from os import environ
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

CONTENT_BUCKET_NAME = environ["CONTENT_BUCKET_NAME"]
CONTENT_METADATA_TB_NAME = environ["CONTENT_METADATA_TB_NAME"]
CONTENT_METADATA_TB_PK = "username"
CONTENT_METADATA_TB_SK = "uuid"

USER_TB_NAME = environ["USER_TB_NAME"]
USER_TB_PK = "username"

ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'

ENDPOINT = environ["ENDPOINT"]
if "ENDPOINT" not in environ:
    raise Exception("Please add ENDPOINT to env")

session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3_cli = session.client('s3', endpoint_url=ENDPOINT)
dynamo_cli = session.client('dynamodb', endpoint_url=ENDPOINT)


def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }


def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v)
        for k, v in dynamo_obj.items()
    }


# https://stackoverflow.com/a/68409773
def base64url_decode(input):
    return base64.urlsafe_b64decode(input + '==')


def base64url_encode(input):
    stringAsBytes = input.encode('ascii')
    stringAsBase64 = base64.urlsafe_b64encode(stringAsBytes).decode('utf-8').replace('=', '')
    return stringAsBase64


def verify_user(token: str) -> None:
    pass


def http_response(body, status_code: int) -> dict:
    return {
        "body": json.dumps(body, default=str),
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json"
        }
    }

def jwt_decode(headers: Dict) -> str:
    auth_header: str = headers['Authorization']
    parts = auth_header.split()
    jwt = parts[1]

    jwt_body_str: str = jwt.split('.')[1]
    jwt_body: Dict = json.loads(base64url_decode(jwt_body_str))
    username = jwt_body['username']

    return username


def owns_that_file(username: str, file_uuid: str) -> bool:
    key = {
        CONTENT_METADATA_TB_PK: username,
        CONTENT_METADATA_TB_SK: file_uuid
    }

    response = dynamo_cli.get_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Key=python_obj_to_dynamo_obj(key)
    )

    if 'Item' not in response:
        return False
    return True

def user_exists(username: str) -> bool:
    key = {
        USER_TB_PK: username,
    }

    response = dynamo_cli.get_item(
        TableName=USER_TB_NAME,
        Key=python_obj_to_dynamo_obj(key)
    )

    if 'Item' not in response:
        return False
    return True