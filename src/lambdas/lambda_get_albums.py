from .common import *


def lambda_get_albums(event: dict, context):
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    result = get_albums(username)

    return http_response(result, 200)