from .common import *


def lambda_family_reject(event: dict, context):
    body: dict = json.loads(event["body"])
    headers: dict = event['headers']
    username: str = jwt_decode(headers)

    sharing_to_username = body[FAMILY_VERIFICATION_TB_SK]
    statement = f"""
        DELETE FROM {USER_TB_NAME}
        WHERE
            {USER_TB_PK} = ?
    """
    dynamo_cli.execute_statement(
        Statement=statement,
        Parameters=python_obj_to_dynamo_obj([sharing_to_username])
    )

    statement = f"""
        DELETE FROM {FAMILY_VERIFICATION_TB_NAME}
        WHERE
            {FAMILY_VERIFICATION_TB_PK} = ?
                    AND
            {FAMILY_VERIFICATION_TB_SK} = ?
    """
    dynamo_cli.execute_statement(
        Statement=statement,
        Parameters=python_obj_to_dynamo_obj([username, sharing_to_username])
    )
    return http_response(None, 204)
