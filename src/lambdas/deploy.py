import os
from typing import List, Tuple
import boto3

# TODO: Use src.service.session - but then relative imports become an issue.
ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'
ENDPOINT = 'http://localhost.localstack.cloud:4566'

session = boto3.Session(aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY,
                        region_name=REGION)
lambda_cli = session.client('lambda', endpoint_url=ENDPOINT)


def get_zips() -> List[Tuple[str, str]]:
    """
    Get filenames of all zipped up lambdas in this directory.
    """

    fnames = []
    for file in os.listdir("."):
        if file.endswith(".zip"):
            fullpath = os.path.join(".", file)
            just_name = file.split(".")[0]
            fnames.append((fullpath, just_name))
    return fnames


def update_lambda(fname: Tuple[str, str]):
    fullpath = fname[0]
    just_name = fname[1]
    lambda_name = f'{just_name}'

    print(fullpath, lambda_name)
    with open(fullpath, 'rb') as f:
        lambda_cli.update_function_code(
            FunctionName=lambda_name,
            ZipFile=f.read(),
        )


def main():
    zip_names = get_zips()

    for zip_fname in zip_names:
        update_lambda(zip_fname)


if __name__ == "__main__":
    main()