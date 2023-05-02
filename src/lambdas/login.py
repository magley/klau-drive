import jwt
from src.lambdas.session import dynamo_cli
from botocore.exceptions import ClientError
from src.lambdas.register_user import TB_USER_NAME, TB_USER_PK

SECRET = "verysecret"


class NoSuchUserException(Exception):
    pass


def login(username: str, password: str):
    try:
        response = dynamo_cli.get_item(
            TableName=TB_USER_NAME,
            # TODO: not good to have unhashed like this
            Key={TB_USER_PK: {"S": username}}
        )
        user = response.get("Item")
        print(user)
        if user is None or user["password"]["S"] != password:
            raise NoSuchUserException("No such user with that password: " + username)
        # TODO: might need more data in jwt
        return jwt.encode({username: username}, SECRET, algorithm="HS256")
    except ClientError as e:
        # TODO: should never get here
        print(e)
        print(e.response["Error"]["Code"])
