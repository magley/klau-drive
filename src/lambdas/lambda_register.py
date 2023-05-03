from typing import Dict
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError
import boto3


ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'
ENDPOINT = 'http://host.docker.internal:4566'

TB_USER_NAME = 'user'
TB_USER_PK = 'username'



"""
awslocal lambda create-function --function-name register --zip-file fileb://register.zip --runtime python3.9 --handler lambda_register.lambda_register --role arn:aws:iam::000000000000:role/LambdaBasic
awslocal lambda update-function-configuration --function-name register --timeout 5
awslocal lambda update-function-code --function-name register --zip-file fileb://register.zip
awslocal lambda invoke --function-name register  --payload file://in.json ./out.json
"""



session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
dynamo_cli = session.client('dynamodb', endpoint_url=ENDPOINT)


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


def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }


def lambda_register(event: Dict, context):
    body: Dict = event['body']
    user_data: Dict = body['user']
    user_data_ddb: Dict = python_obj_to_dynamo_obj(user_data)

    create_table_if_not_exists(TB_USER_NAME, TB_USER_PK, None)
    try:
        dynamo_cli.put_item(
            TableName=TB_USER_NAME,
            Item=user_data_ddb,
            ConditionExpression='attribute_not_exists(username)'
        )

        return {
            "body": {
                "status": 200,
                "message": "",
            }
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                "body": {
                    "status": 400,
                    "message": "Username already taken"
                }
            }
        else:
            raise e