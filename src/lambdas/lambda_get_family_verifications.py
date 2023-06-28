from .common import *


def get_family_verifications_for(username: str):
    statement = f"""
        SELECT * FROM {FAMILY_VERIFICATION_TB_NAME}
        WHERE
            {FAMILY_VERIFICATION_TB_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([username])
    response = dynamo_cli.execute_statement(
        Statement=statement,
        Parameters=parameters
    )
    family_verifications = []
    for o in response["Items"]:
        obj = dynamo_obj_to_python_obj(o)
        family_verifications.append(obj)
    return family_verifications


def lambda_get_family_verifications(event: dict, context):
    username: str = jwt_decode(event["headers"])
    if not user_exists(username):
        return http_response("Forbidden", 401)
    result = get_family_verifications_for(username)
    return http_response(result, 200)
