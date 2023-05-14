import os
from typing import List, Tuple
import boto3
from common_deploy import *


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