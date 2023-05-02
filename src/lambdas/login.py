from src.lambdas.session import dynamo_cli
from botocore.exceptions import ClientError
from register_user import TB_USER_NAME, TB_USER_PK


def login(username: str, password: str):
    try:
        response = dynamo_cli.get_item(
            TableName=TB_USER_NAME,
            Key={TB_USER_PK: username}
        )
        print(response)
        return None
    except ClientError as e:
        print(e)
        print(e.response["Error"]["Code"])
