import json

from .common import *


def get_all_garbage(username: str):
    statement = f"""
        SELECT * FROM {TB_GARBAGE_COLLECTOR_NAME}
        WHERE
            {TB_GARBAGE_COLLECTOR_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([username])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    res = []
    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        res.append(obj)
    return res


def lambda_collect_garbage(event: dict, context):
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    success = 0
    fail = 0
    for item in get_all_garbage(username):
        uuid = item[TB_GARBAGE_COLLECTOR_SK]
        try:
            sqs_cli.send_message(QueueUrl=GARBAGE_QUEUE_URL,
                                 MessageBody=json.dumps({"username": username, "uuid": uuid}))
            success += 1
        except Exception as e:
            # this will probably never fail
            fail += 1
            raise e

    return http_response({"success": success, "fail": fail}, 200)