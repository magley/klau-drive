import base64
import hashlib
import hmac
import json
from typing import Dict
import boto3


ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'
ENDPOINT = 'http://host.docker.internal:4566'

TB_USER_NAME = 'user'
TB_USER_PK = 'username'
SECRET = "verysecret"

session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
dynamo_cli = session.client('dynamodb', endpoint_url=ENDPOINT)

"""
awslocal lambda create-function --function-name login --zip-file fileb://login.zip --runtime python3.9 --handler lambda_login.lambda_login --role arn:aws:iam::000000000000:role/LambdaBasic
awslocal lambda update-function-configuration --function-name login --timeout 3
awslocal lambda update-function-code --function-name login --zip-file fileb://login.zip
awslocal lambda invoke --function-name login  --payload file://in.json ./out.json
"""

# https://stackoverflow.com/a/68409773

def base64url_decode(input):
    return base64.urlsafe_b64decode(input+'==')


def base64url_encode(input):
    stringAsBytes = input.encode('ascii')
    stringAsBase64 = base64.urlsafe_b64encode(stringAsBytes).decode('utf-8').replace('=','')
    return stringAsBase64 


def jwt_creator(username: str):
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        'username': username,
    }
    secret_key = SECRET
    total_params = str(base64url_encode(json.dumps(header))) + '.' + str(base64url_encode(json.dumps(payload)))
    signature = hmac.new(secret_key.encode(), total_params.encode(), hashlib.sha256).hexdigest()
    token = total_params + '.' + str(base64url_encode(signature))
    return token


def lambda_login(event: Dict, context):
    body: Dict = event['body']
    username = body['username']
    password = body['password']

    response = dynamo_cli.get_item(
        TableName = TB_USER_NAME,
        Key={TB_USER_PK: {"S": username}} # TODO: not good to have it unhashed
    )

    user = response.get("Item")
    if user is None or user["password"]["S"] != password:
        return {
            "body": None
        }
    
    return {
        "body": {
            "token": jwt_creator(username),
        },
    }