from botocore.exceptions import ClientError

def print_objects(s3, bucket):
    try:
        for obj in s3.Bucket(bucket).objects.all():
            print(obj.key)

    except ClientError as err:
        print('Unable to list bucket: {0}. '.format(bucket) + str(err))

    return