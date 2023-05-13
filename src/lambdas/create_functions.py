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


def create_function(fname: Tuple[str, str]) -> None:
    fullpath = fname[0]
    just_name = fname[1]
    lambda_name = f'lambda_{just_name}'

    print(fullpath, just_name)
    with open(fullpath, 'rb') as f:
        lambda_cli.create_function(
            FunctionName=just_name,
            Runtime='python3.9',
            Role='arn:aws:iam::000000000000:role/LambdaBasic',
            Handler=f'{lambda_name}.{lambda_name}',
            Timeout=30,
            PackageType='Zip',
            Code={
                'ZipFile': f.read(),
            }
        )


def main():
    zip_names = get_zips()

    for zip_fname in zip_names:
        create_function(zip_fname)


if __name__ == "__main__":
    main()