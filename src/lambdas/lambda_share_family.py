from .lambda_share import *


def lambda_share_family(event: dict, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        username = body["username_who_shares"]
        share_single_obj(username, body)
