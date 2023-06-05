
from botocore.exceptions import ClientError
from .common import *


def lambda_register(event: dict, context):
    body: dict = json.loads(event['body'])
    user_data: dict = body
    user_data_ddb: dict = python_obj_to_dynamo_obj(user_data)

    try:
        dynamo_cli.put_item(
            TableName=USER_TB_NAME,
            Item=user_data_ddb,
            ConditionExpression='attribute_not_exists(username)'
        )

        return http_response(None, 204)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return http_response({"message": "Username already taken"}, 400)
        else:
            return http_response({"message": e.response['Error']['Code']}, 400)