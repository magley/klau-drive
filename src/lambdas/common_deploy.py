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
apigateway_cli = session.client('apigateway', endpoint_url=ENDPOINT)


def get_zips() -> List[Tuple[str, str]]:
    """
    Get filenames of all zipped up lambdas in this directory.
    Each file is representeed by a tuple (full_file_path, just_name).
    """

    fnames = []
    for file in os.listdir("."):
        if file.endswith(".zip"):
            fullpath = os.path.join(".", file)
            just_name = file.split(".")[0]
            fnames.append((fullpath, just_name))
    return fnames


def get_lambda_module_files() -> List[Tuple[str, str]]:
    """
    Get filenames of all lambdas in this directory.
    By convention, the module must be a .py and must begin with "lambda_".
    Each file is representeed by a tuple (full_file_path, just_name).
    """

    fnames = []
    for file in os.listdir("."):
        if file.startswith("lambda_") and file.endswith(".py"):
            fullpath = os.path.join(".", file)
            just_name = file.split(".")[0]
            fnames.append((fullpath, just_name))
    return fnames