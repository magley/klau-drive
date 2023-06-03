from typing import Dict
from .common import *


def lambda_list_files(event: Dict, context):
    body: Dict = json.loads(event['body'])
    headers: Dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)

    response = dynamo_cli.query(
        TableName=CONTENT_METADATA_TB_NAME,
        KeyConditionExpression=f'{CONTENT_METADATA_TB_PK} = :pk',
        ExpressionAttributeValues={
            ':pk': {
                'S': username,
            },
        }
    )

    items = response['Items']

    result = []
    for o in items:
        result.append(dynamo_obj_to_python_obj(o))

    return http_response(result, 200)