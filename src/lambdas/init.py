from src.lambdas.session import dynamo_cli, s3_cli, s3_res
import src.lambdas.upload_file as upload_file
import src.lambdas.register_user as register_user


def init():
    _init_bucket(upload_file.BUCKET_NAME)
    _init_table(upload_file.TB_META_NAME, upload_file.TB_META_PK, upload_file.TB_META_SK)
    _init_table(register_user.TB_USER_NAME, register_user.TB_USER_PK, None)


def _init_bucket(bucket_name):
    bucket = s3_res.Bucket(bucket_name)
    try:
        bucket.objects.all().delete()
        bucket.delete()
    except Exception as e:
        pass

    s3_cli.create_bucket(Bucket=bucket_name)


def _init_table(table_name, pk, sk):
    try:
        dynamo_cli.delete_table(TableName=table_name)
    except Exception as e:
        pass

    attrdef = [
        {
            'AttributeName': pk,
            'AttributeType': 'S',
        },
    ]
    keyschema = [
        {
            'AttributeName': pk,
            'KeyType': 'HASH',
        }
    ]

    if sk is not None:
        attrdef.append({
            'AttributeName': sk,
            'AttributeType': 'S',
        })
        keyschema.append({
            'AttributeName': sk,
            'KeyType': 'RANGE',
        })

    dynamo_cli.create_table(
        TableName=table_name,
        AttributeDefinitions=attrdef,
        KeySchema=keyschema,
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
    )
