from dataclasses import dataclass, asdict
from datetime import date
from dynamodb_json import json_util
from src.lambdas.session import dynamo_cli


@dataclass
class User:
    name: str
    surname: str
    date_of_birth: date
    username: str
    email: str
    password: str


TB_USER_NAME = 'user'
TB_USER_PK = 'username'


def register_user(user: User):
    user_ddb = json_util.dumps(asdict(user), as_dict=True)
    dynamo_cli.put_item(
        TableName=TB_USER_NAME,
        Item=user_ddb,
        ConditionExpression='attribute_not_exists(username) AND attribute_not_exists(email)'
    )
