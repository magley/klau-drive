from .common import *


def get_shared(username: str):
    statement = f"""
        SELECT * FROM {TB_SHARED_WITH_ME_NAME}
        WHERE
            {TB_SHARED_WITH_ME_PK}=?
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


def lambda_get_shared(event: dict, context):
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    result = get_shared(username)

    return http_response(result, 200)