from src.service.session import dynamo_cli, s3_cli, s3_res


def create_bucket_if_not_exists(bucket_name):
    # s3_cli.create_bucket is idempotent.
    s3_cli.create_bucket(Bucket=bucket_name)


def create_table_if_not_exists(table_name, pk, sk):
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

    try:
        dynamo_cli.create_table(
            TableName=table_name,
            AttributeDefinitions=attrdef,
            KeySchema=keyschema,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )
    except dynamo_cli.exceptions.ResourceInUseException:
        pass


def delete_bucket(bucket_name):
    bucket = s3_res.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()


def delete_table(table_name):
    dynamo_cli.delete_table(TableName=table_name)
