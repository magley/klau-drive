import boto3

# TODO: Use src.service.session - but then relative imports become an issue.
ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'
ENDPOINT = 'http://localhost.localstack.cloud:4566'

session = boto3.Session(aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY,
                        region_name=REGION)
apigateway_cli = session.client('apigateway', endpoint_url=ENDPOINT)



def main():
    response = apigateway_cli.create_rest_api(
        name='kalu-drive API',
        description='klau-drive REST API',
    )
    REST_API_ID = response['id']

    response = apigateway_cli.get_resources(
        restApiId=REST_API_ID,
    )
    PARENT_ID = response['items'][0]['id']

    response = apigateway_cli.create_resource(
        restApiId=REST_API_ID,
        parentId=PARENT_ID,
        pathPart='{id}'
    )
    RESOURCE_ID = response['id']

    response = apigateway_cli.put_method(
        restApiId=REST_API_ID,
        resourceId=RESOURCE_ID,
        httpMethod='GET',
        authorizationType='NONE',
        requestParameters={
            'method.request.path.somethingId': True
        },
    )

    func_uri = 'arn:aws:lambda:us-east-1:000000000000:function:list_files'
    response = apigateway_cli.put_integration(
        restApiId=REST_API_ID,
        resourceId=RESOURCE_ID,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        passthroughBehavior='WHEN_NO_MATCH',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{func_uri}/invocations',
    )

    response = apigateway_cli.create_deployment(
        restApiId=REST_API_ID,
        stageName='test',
    )

    print("Rest API ID:")
    print(REST_API_ID)
    print("Call GET on:")
    print(f'http://localhost:4566/restapis/{REST_API_ID}/test/_user_request_/HowMuchIsTheFish')


if __name__ == "__main__":
    main()