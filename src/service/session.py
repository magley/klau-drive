from os import environ

if "BASE_URL" not in environ:
    raise Exception("Please add BASE_URL to env")
BASE_URL = environ["BASE_URL"]
print("Make sure to change BASE_URL in your env when generating a new one or restarting localstack.")
