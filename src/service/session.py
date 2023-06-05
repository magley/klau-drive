from os import environ
import jwt

if "BASE_URL" not in environ:
    raise Exception("Please add BASE_URL to env")
BASE_URL = environ["BASE_URL"]
print("Make sure to change BASE_URL in your env when generating a new one or restarting localstack.")


TOKEN_FILENAME = "user_token.txt"


def get_username() -> str:
    token = ""
    try:
        token = get_jwt()
    except FileNotFoundError:
        pass

    decoded = jwt.decode(token, options={"verify_signature": False})
    return decoded['username']


def get_jwt() -> str:
    with open(TOKEN_FILENAME, "r") as token_file:
        return token_file.readline().strip()