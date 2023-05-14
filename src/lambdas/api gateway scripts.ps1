# Make sure to change all the IDs when running it yourself.

awslocal apigateway create-rest-api --name 'klau-drive-api'

awslocal apigateway get-resources --rest-api-id q7esmv1ism

awslocal apigateway create-resource `
    --rest-api-id q7esmv1ism `
    --parent-id gdtuzm8vbc `
    --path-part "{somethingId}"


awslocal apigateway put-method `
    --rest-api-id q7esmv1ism `
    --resource-id qnei36mqjk `
    --http-method GET `
    --request-parameters "method.request.path.somethingId=true" `
    --authorization-type "NONE"

awslocal apigateway put-integration `
    --rest-api-id q7esmv1ism `
    --resource-id qnei36mqjk `
    --http-method GET `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:list_files/invocations `
    --passthrough-behavior WHEN_NO_MATCH


awslocal apigateway create-deployment `
 --rest-api-id q7esmv1ism `
 --stage-name test

http://localhost:4566/restapis/q7esmv1ism/test/_user_request_/HowMuchIsTheFish
                               ^^^^^^^^^^
                                    