# By convention, every lambda function imports this as
# from common import *
# So mind the name clashing!
import json
import boto3
from os import environ
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

CONTENT_BUCKET_NAME = environ["CONTENT_BUCKET_NAME"]
CONTENT_METADATA_TB_NAME = environ["CONTENT_METADATA_TB_NAME"]
CONTENT_METADATA_TB_PK = "name"

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


def http_response(body, status_code: int) -> dict:
    return {
        "body": json.dumps(body, default=str),  # TODO: API Gateway does NOT
        # allow the value to be just `body` i.e. a Python object (e.g. a list),
        # and we HAVE TO convert it into a json string. This becomes a problem
        # on the frontend where we then have to do json.loads(p['body']) even
        # though p was already `json.loads`-ed. It's pointless. If we try to
        # move the json.dumps(...) to wrap this entire return value i.e. the
        # whole dictionary, then we would have to do json.loads() twice on the
        # frontend when fetching lambda response payload.
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json"
        }
    }
