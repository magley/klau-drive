from .common import *


def get_sharing(owner: str, sharing_with: str):
    statement = f"""
        SELECT * FROM {TB_SHARED_WITH_ME_NAME}
        WHERE
            {TB_SHARED_WITH_ME_PK}=?
                AND
            {TB_SHARED_WITH_ME_FIELD_OWNER}=?
    """
    parameters = python_obj_to_dynamo_obj([sharing_with, owner])

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
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    if "username" not in body:
        return http_response("No username", 400)
    sharing_with: str = body['username']
    if len(sharing_with.strip()) == 0:
        return http_response("Username cannot be empty", 400)
 
    result = get_sharing(owner=username, sharing_with=sharing_with)

    return http_response(result, 200)