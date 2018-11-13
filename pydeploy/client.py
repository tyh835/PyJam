import boto3
from botocore.exceptions import ClientError

def set_client(region=None, profile=None, **kwargs):
    session = boto3.Session()
    ec2 = session.resource('ec2')

    if profile:
        session = boto3.Session(profile_name=profile)

    if region:
        ec2 = session.resource('ec2', region_name=region)

    return ec2