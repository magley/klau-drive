import os

TOKEN_FILENAME = "user_token.txt"


def write_token(jwt: str):
    with open(TOKEN_FILENAME, "w") as token_file:
        print(jwt, file=token_file)


def read_token():
    jwt = ""
    # TODO: stop user illegal tampering by checking if really a token in the file?
    try:
        with open(TOKEN_FILENAME, "r") as token_file:
            jwt = token_file.readline().strip()
    except FileNotFoundError:
        pass
    return jwt


def delete_token():
    if os.path.exists(TOKEN_FILENAME):
        os.remove(TOKEN_FILENAME)
        return True
    return False
