### How to deploy:

Set env vars on windows (null on end is not 100% necessary):

`$env:FOO='BAR'; .\myscript; $env:FOO=$null`

Navigate to root directory (where src/ is, not inside of it)

First run this to pickup serverless: `npm ci`

Run: `ENDPOINT=<your endpoint> npm run sls deploy`

Example: `ENDPOINT='http://host.docker.internal:4566' npm run sls deploy`

(it's this on linux: http://172.17.0.2:4566)

You can use `serverless deploy` instead of `npm run sls deploy` if you have it global

### How to run:

Navigate to root directory (where src/ is, not inside of it)

Install the requirements: `python -m pip install -r requirements.txt`

Run: `BASE_URL=<your deployed url> python -m src.main`

Example: `BASE_URL='http://localhost:4566/restapis/3ojfyrsn1f/dev/_user_request_' python -m src.main`


# Win

$env:ENDPOINT='http://host.docker.internal:4566'
npm ci
localstack start
npm run sls deploy
$env:BASE_URL=
python -m src.main
npm run sls -- deploy function --function deleteFile