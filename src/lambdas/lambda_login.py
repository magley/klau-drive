import base64
import hashlib
import hmac
import json
from typing import Dict
from common import *


SECRET = "verysecret"

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
    body: Dict = json.loads(event['body'])
    username = body['username']
    password = body['password']

    response = dynamo_cli.get_item(
        TableName = USER_TB_NAME,
        Key={USER_TB_PK: {"S": username}} # TODO: not good to have it unhashed
    )

    user = response.get("Item")
    if user is None or user["password"]["S"] != password:
        return http_response("Wrong username or password", 401)
    
    return http_response({ "token": jwt_creator(username) }, 200)