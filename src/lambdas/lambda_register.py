from typing import Dict
from botocore.exceptions import ClientError
from common import *

"""
awslocal lambda create-function --function-name register --zip-file fileb://register.zip --runtime python3.9 --handler lambda_register.lambda_register --role arn:aws:iam::000000000000:role/LambdaBasic
awslocal lambda update-function-configuration --function-name register --timeout 50
awslocal lambda update-function-code --function-name register --zip-file fileb://register.zip
awslocal lambda invoke --function-name register  --payload file://in.json ./out.json
"""

def lambda_register(event: Dict, context):
    body: Dict = event['body']
    user_data: Dict = body['user']
    user_data_ddb: Dict = python_obj_to_dynamo_obj(user_data)

    create_table_if_not_exists(USER_TB_NAME, USER_TB_PK, USER_TB_SK)
    try:
        dynamo_cli.put_item(
            TableName=USER_TB_NAME,
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
            return {
                "body": {
                    "status": 400,
                    "message": e.response['Error']['Code']
                }
            }