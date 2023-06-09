from botocore.exceptions import ClientError
from .common import *


def lambda_register_without_family(event: dict, context):
    user_data: dict = event
    user_data["activated"] = True
    user_data_ddb: dict = python_obj_to_dynamo_obj(user_data)

    default_album_data: dict = {
        TB_USER_ALBUMS_PK: user_data['username'],
        TB_USER_ALBUMS_SK: f'{user_data["username"]}_root',
        TB_USER_ALBUMS_FIELD_NAME: f"{user_data['username']}'s drive",
    }
    default_album_data_ddb: dict = python_obj_to_dynamo_obj(default_album_data)

    try:
        # TODO: consistency rollbacks
        dynamo_cli.put_item(
            TableName=USER_TB_NAME,
            Item=user_data_ddb,
            ConditionExpression='attribute_not_exists(username)'
        )
        dynamo_cli.put_item(
            TableName=TB_USER_ALBUMS_NAME,
            Item=default_album_data_ddb
        )

        return http_response(None, 204)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return http_response({"message": "Username already taken"}, 400)
        else:
            return http_response({"message": e.response['Error']['Code']}, 400)
