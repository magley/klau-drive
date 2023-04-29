from dataclasses import dataclass, asdict
from datetime import date
from dynamodb_json import json_util
from src.lambdas.session import dynamo_cli
from botocore.exceptions import ClientError


@dataclass
class User:
    name: str | None
    surname: str | None
    date_of_birth: str | None
    username: str
    email: str | None
    password: str


TB_USER_NAME = 'user'
TB_USER_PK = 'username'


def register_user(user: User) -> str | None:
    user_ddb = json_util.dumps(asdict(user), as_dict=True)
    try:
        dynamo_cli.put_item(
            TableName=TB_USER_NAME,
            Item=user_ddb,
            ConditionExpression='attribute_not_exists(username)'
        )
        return None
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return 'Username already taken'
        else:
            raise e