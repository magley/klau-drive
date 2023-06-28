from .common import *


def lambda_register(event: dict, context):
    user_data: dict = json.loads(event['body'])
    if "username" not in user_data or not user_data["username"]:
        return http_response({"message": "Need username to register"}, 400)
    if "password" not in user_data or not user_data["password"]:
        return http_response({"message": "Need password to register"}, 400)
    if "family" not in user_data or not user_data["family"]:
        user_data["family"] = ""  # just in case
    # TODO: does this need some stuff for error handling?
    stepfunctions_cli.start_execution(stateMachineArn=REGISTER_STEP, input=json.dumps(user_data, default=str))
    return http_response(None, 204)
