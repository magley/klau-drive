from .common import *


def get_albums(username: str):
    statement = f"""
        SELECT * FROM {TB_USER_ALBUMS_NAME}
        WHERE
            {TB_USER_ALBUMS_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([username])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    albums = []
    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        albums.append(obj)
    return albums


def lambda_get_albums(event: dict, context):
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    result = get_albums(username)

    return http_response(result, 200)