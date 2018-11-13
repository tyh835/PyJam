import boto3
from botocore.exceptions import ClientError

def set_client(profile=None, **kwargs):
    session = boto3.Session()

    if profile:
        session = boto3.Session(profile_name=profile)

    s3 = session.resource('s3')

    return s3


def print_objects(s3, bucket):
    try:
        for obj in s3.Bucket(bucket).objects.all():
            print(obj.key)

    except ClientError as err:
        print('Unable to list bucket: {0}. '.format(bucket) + str(err))

    return