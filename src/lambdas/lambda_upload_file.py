import base64
import io
from typing import Dict
from boto3.dynamodb.types import TypeSerializer
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
awslocal lambda create-function --function-name upload_file --zip-file fileb://upload_file.zip --runtime python3.9 --handler lambda_upload_file.lambda_upload_file --role arn:aws:iam::000000000000:role/LambdaBasic
awslocal lambda update-function-configuration --function-name upload_file --timeout 900
awslocal lambda update-function-code --function-name upload_file --zip-file fileb://upload_file.zip
awslocal lambda invoke --function-name upload_file --payload file://in.json ./out.json
"""

def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }


# TODO: Create a lambda that initializes the dynamodb table and s3 bucket.
def create_bucket_if_not_exists(bucket_name):
    s3_cli.create_bucket(Bucket=bucket_name)


def create_table_if_not_exists(table_name, pk, sk):
    attrdef = [
        {
            'AttributeName': pk,
            'AttributeType': 'S',
        },
    ]
    keyschema = [
        {
            'AttributeName': pk,
            'KeyType': 'HASH',
        }
    ]

    if sk is not None:
        attrdef.append({
            'AttributeName': sk,
            'AttributeType': 'S',
        })
        keyschema.append({
            'AttributeName': sk,
            'KeyType': 'RANGE',
        })

    try:
        dynamo_cli.create_table(
            TableName=table_name,
            AttributeDefinitions=attrdef,
            KeySchema=keyschema,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )
    except dynamo_cli.exceptions.ResourceInUseException:
        pass


def lambda_upload_file(event: Dict, context):
    body: Dict = event['body']
    metadata: Dict = body['metadata']
    metadata_dynamojson: str = python_obj_to_dynamo_obj(metadata)
    data: bytes = base64.b64decode(body['data'])

    create_bucket_if_not_exists(BUCKET_NAME)
    create_table_if_not_exists(TB_META_NAME, TB_META_PK, TB_META_SK)

    dynamo_cli.put_item(
        TableName=TB_META_NAME,
        Item=metadata_dynamojson
    )

    s3_cli.upload_fileobj(
        Fileobj=io.BytesIO(data),
        Bucket=BUCKET_NAME,
        Key=metadata['name']
    )

    return { "metadata": metadata, "data": str(data) }