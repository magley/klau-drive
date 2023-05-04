import boto3

ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'
ENDPOINT = 'http://localhost.localstack.cloud:4566'

session = boto3.Session(aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY,
                        region_name=REGION)
s3_cli = session.client('s3', endpoint_url=ENDPOINT)
s3_res = session.resource("s3", endpoint_url=ENDPOINT)
dynamo_cli = session.client('dynamodb', endpoint_url=ENDPOINT)
lambda_cli = session.client('lambda', endpoint_url=ENDPOINT)