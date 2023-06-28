from .common import *


def lambda_collect_piece_of_garbage(event: dict, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        username = body["username"]
        if not user_exists(username):
            return http_response("Forbidden", 401)
        uuid = body["uuid"]
        s3_cli.delete_object(
            Bucket=CONTENT_BUCKET_NAME,
            Key=uuid
        )
        dynamo_cli.delete_item(
            TableName=TB_GARBAGE_COLLECTOR_NAME,
            Key=python_obj_to_dynamo_obj({
                TB_GARBAGE_COLLECTOR_PK: username,
                TB_GARBAGE_COLLECTOR_SK: uuid
            })
        )
