from .common import *


def delete_single_file(username: str, uuid: str):
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
            delete_single_file(username, uuid)
            success += 1
        except Exception:
            fail += 1

    return http_response({"success": success, "fail": fail}, 200)