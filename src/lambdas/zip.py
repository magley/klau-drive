import zipfile
import os
from typing import List, Tuple
from common_deploy import *


COMMON_FNAME = "./common.py"


def zip_file(fname: Tuple[str, str]):
    fullpath = fname[0]
    just_name = fname[1]
    zip_name = just_name[len("lambda_"):] # Minus the 'lambda_' prefix.

    print(f'{zip_name}.zip')

    with zipfile.ZipFile(f'{zip_name}.zip', mode='w') as zf:
        zf.write(fullpath)
        zf.write(COMMON_FNAME)


def main():
    fnames = get_lambda_module_files()

    for fname_pair in fnames:
        zip_file(fname_pair)


if __name__ == "__main__":
    main()