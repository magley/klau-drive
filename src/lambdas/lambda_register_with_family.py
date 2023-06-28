from botocore.exceptions import ClientError
from .common import *


def lambda_register_with_family(event: dict, context):
    user_data: dict = event
    if "family" not in user_data:
        return http_response({"message": "Missing family for register"}, 400)
    user_data["activated"] = False
    user_data_ddb: dict = python_obj_to_dynamo_obj(user_data)
    if not user_exists(user_data["family"]):
        return http_response("No user exists for family registration", 400)

    default_album_data: dict = {
        TB_USER_ALBUMS_PK: user_data['username'],
        TB_USER_ALBUMS_SK: f'{user_data["username"]}_root',
        TB_USER_ALBUMS_FIELD_NAME: 'root'
    }
    default_album_data_ddb: dict = python_obj_to_dynamo_obj(default_album_data)

    family_data_ddb = python_obj_to_dynamo_obj({
        FAMILY_VERIFICATION_TB_PK: user_data["family"],
        FAMILY_VERIFICATION_TB_SK: user_data["username"],
    })

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
        dynamo_cli.put_item(
            TableName=FAMILY_VERIFICATION_TB_NAME,
            Item=family_data_ddb
        )

        send_email(user_data["family"], f"A family member is registering: {user_data['username']}",
                   "Family member registering")
        return http_response(None, 204)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return http_response({"message": "Username already taken"}, 400)
        else:
            return http_response({"message": e.response['Error']['Code']}, 400)