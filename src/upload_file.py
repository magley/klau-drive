import json
from pathlib import Path
import boto3

ACCESS_KEY = 'test'
SECRET_KEY = 'test'
ENDPOINT = 'http://localhost.localstack.cloud:4566'
BUCKET_NAME = "content"

session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3_cli = session.client('s3', endpoint_url=ENDPOINT)


def upload_file_s3(fname: str, key: str):
    s3_cli.upload_file(
        Filename=fname,
        Bucket=BUCKET_NAME,
        Key=key
    )

def Init():
    s3_cli.create_bucket(Bucket=BUCKET_NAME)


def ListFiles():
    response = s3_cli.list_objects(Bucket=BUCKET_NAME)
    return response.get('Contents')


def UploadFile(fname: str):
    key = Path(fname).stem
    upload_file_s3(fname, key)



UploadFile("./upload_file.py")

for file in ListFiles():
    print(file)