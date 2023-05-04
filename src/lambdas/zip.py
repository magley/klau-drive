import zipfile
import os
from typing import List, Tuple


COMMON_FNAME = "./common.py"


def get_lambdas() -> List[Tuple[str, str]]:
    """
    Get filenames of all lambdas in this directory.
    By convention, the module must be a .py and must begin with "lambda_".
    """

    fnames = []
    for file in os.listdir("."):
        if file.startswith("lambda_") and file.endswith(".py"):
            fullpath = os.path.join(".", file)
            just_name = file.split(".")[0]
            fnames.append((fullpath, just_name))
    return fnames


def zip_file(fname: Tuple[str, str]):
    fullpath = fname[0]
    just_name = fname[1]
    zip_name = just_name[len("lambda_"):] # Minus the 'lambda_' prefix.

    print(f'{zip_name}.zip')

    with zipfile.ZipFile(f'{zip_name}.zip', mode='w') as zf:
        zf.write(fullpath)
        zf.write(COMMON_FNAME)


def main():
    fnames = get_lambdas()

    for fname_pair in fnames:
        zip_file(fname_pair)


if __name__ == "__main__":
    main()