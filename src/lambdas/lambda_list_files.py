import base64
from dataclasses import dataclass
from datetime import datetime
import io
import json
from typing import Dict, List
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
import boto3

BUCKET_NAME = "content"
TB_META_NAME = 'file_meta'
TB_META_PK = 'name'
TB_META_SK = None

ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'
ENDPOINT = 'http://host.docker.internal:4566' # Not 'localhost.localstack.cloud:4566'

session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3_cli = session.client('s3', endpoint_url=ENDPOINT)
dynamo_cli = session.client('dynamodb', endpoint_url=ENDPOINT)


"""
awslocal lambda create-function --function-name list_files --zip-file fileb://list_files.zip --runtime python3.9 --handler lambda_list_files.lambda_list_files --role arn:aws:iam::000000000000:role/LambdaBasic
awslocal lambda update-function-configuration --function-name list_files --timeout 180
awslocal lambda update-function-code --function-name list_files --zip-file fileb://list_files.zip
awslocal lambda invoke --function-name list_files ./out.json
"""


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

def dynamo_to_py(dynamo) -> Dict:
    des = TypeDeserializer()
    return {
        k: des.deserialize(v) for k, v in dynamo.items()
    }


def lambda_list_files(event: Dict, context):
    result = []

    try:
        response = s3_cli.list_objects(Bucket=BUCKET_NAME)
    except s3_cli.exceptions.NoSuchBucket:
        return result

    contents = response.get('Contents')
    if contents is None:
        return result

    for s3_file in contents:
        dynamo_key = {TB_META_PK: s3_file['Key']}
        dynamo_key = python_obj_to_dynamo_obj(dynamo_key)
        dynamo_res = dynamo_cli.get_item(TableName=TB_META_NAME, Key=dynamo_key)
        dynamo_item = dynamo_obj_to_python_obj(dynamo_res.get('Item'))

        item = {
            "name":s3_file['Key'],
            "type":dynamo_item.get('type', ''),
            "desc":dynamo_item.get('desc', ''),
            "tags":dynamo_item.get('tags', []),
            "size":dynamo_item.get('size', 0),
            "upload_date":dynamo_item.get('uploadDate', ""),
            "last_modified":dynamo_item.get('modificationDate', ""),
            "creation_date":dynamo_item.get('creationDate', ""),
        }

        result.append(item)
    result = sorted(result, key=lambda item: item['upload_date'], reverse=True)
    
    return {
        "body": result
    }