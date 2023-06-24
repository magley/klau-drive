from .common import *


def get_sharing(username: str):
    statement = f"""
        SELECT * FROM {TB_SHARE_NAME}
        WHERE
            {TB_SHARE_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([username])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    shared_objects = []
    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        shared_objects.append(obj)
    return shared_objects


def lambda_get_sharing(event: dict, context):
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    result = get_sharing(username)

    return http_response(result, 200)