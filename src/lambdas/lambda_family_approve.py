from .common import *


def lambda_family_approve(event: dict, context):
    body: dict = json.loads(event["body"])
    headers: dict = event['headers']
    username: str = jwt_decode(headers)
    sharing_to_username = body[FAMILY_VERIFICATION_TB_SK]

    item = dynamo_cli.get_item(
        TableName=USER_TB_NAME,
        Key={USER_TB_PK: {"S": sharing_to_username}}
    ).get("Item")
    user_data = dynamo_obj_to_python_obj(item)
    user_data["activated"] = True
    dynamo_cli.put_item(
        TableName=USER_TB_NAME,
        Item=python_obj_to_dynamo_obj(user_data),
    )

    albums = get_albums(username)
    for album in albums:
        sqs_cli.send_message(QueueUrl=FAMILY_SHARE_QUEUE_URL,
                             MessageBody=json.dumps({
                                 "username": sharing_to_username,
                                 "uuid": album[TB_USER_ALBUMS_SK],
                                 "is_album": True,
                                 "username_who_shares": username
                             }))
    return http_response(None, 204)
