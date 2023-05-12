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


def create_rest_api(name: str) -> str:
    response = apigateway_cli.create_rest_api(
        name='kalu-drive API',
        description='klau-drive REST API',
    )
    return response['id']


def get_parent_resource_id(rest_api_id: str) -> str:
    response = apigateway_cli.get_resources(
        restApiId=rest_api_id,
    )
    return response['items'][0]['id']


def create_resource(rest_api_id: str, parent_id: str, path_part: str) -> str:
    response = apigateway_cli.create_resource(
        restApiId=rest_api_id,
        parentId=parent_id,
        pathPart=path_part
    )
    return response['id']

def put_method(rest_api_id: str, resource_id: str, method: str, func_uri: str) -> None:
    apigateway_cli.put_method(
        restApiId=rest_api_id,
        resourceId=resource_id,
        httpMethod=method,
        authorizationType='NONE',
        # requestParameters={
        #     'method.request.path.somethingId': True
        # },
    )

    apigateway_cli.put_integration(
        restApiId=rest_api_id,
        resourceId=resource_id,
        httpMethod=method,
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        passthroughBehavior='WHEN_NO_MATCH',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{func_uri}/invocations',
    )

def deploy_api(rest_api_id: str, stage_name: str) -> None:
    apigateway_cli.create_deployment(
        restApiId=rest_api_id,
        stageName=stage_name,
    )


def main():
    STAGE_NAME = 'test'
    REST_API_ID = create_rest_api('klau-drive API')
    PARENT_ID = get_parent_resource_id(REST_API_ID)

    RES_SESSION = create_resource(REST_API_ID, PARENT_ID, 'session')
    print(f'http://localhost:4566/restapis/{REST_API_ID}/{STAGE_NAME}/_user_request_/session')
    put_method(REST_API_ID, RES_SESSION, 'PUT', 'arn:aws:lambda:us-east-1:000000000000:function:login')
    put_method(REST_API_ID, RES_SESSION, 'POST', 'arn:aws:lambda:us-east-1:000000000000:function:register')

    deploy_api(REST_API_ID, STAGE_NAME)

    



if __name__ == "__main__":
    main()