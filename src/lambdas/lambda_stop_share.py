from .common import *


def remove_share_obj(owner: str, uuid: str, username: str):
    statement1 = f"""
        DELETE FROM {TB_SHARED_WITH_ME_NAME}
        WHERE
            {TB_SHARED_WITH_ME_PK} = ?
                AND
            {TB_SHARED_WITH_ME_SK} = ?
                AND
            {TB_SHARED_WITH_ME_FIELD_OWNER} = ?
    """

    parameters1 = python_obj_to_dynamo_obj([username, uuid, owner])

    dynamo_cli.execute_statement(  
        Statement=statement1,
        Parameters=parameters1
    )


def lambda_stop_share(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)

    uuid: str = body['uuid']
    username_to_share_with: str = body['username']
    owner: str = body['owner']

    if owner != username:
        return http_response("Unauthorized", 403)

    remove_share_obj(owner, uuid, username_to_share_with)

    return http_response("No conent", 204)
