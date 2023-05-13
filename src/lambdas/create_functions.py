from typing import Tuple
from common_deploy import *


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