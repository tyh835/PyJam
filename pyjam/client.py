import boto3

def set_client(profile=None, **kwargs):
    session = boto3.Session()

    if profile:
        session = boto3.Session(profile_name=profile)

    s3 = session.resource('s3')

    return s3


