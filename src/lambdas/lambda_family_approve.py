from .common import *


def lambda_family_approve(event: dict, context):
    body: dict = json.loads(event["body"])
    headers: dict = event['headers']
    username: str = jwt_decode(headers)
    sharing_to_username = body[FAMILY_VERIFICATION_TB_SK]
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
