"""Utility functions for S3Client"""

from collections import namedtuple
from botocore.exceptions import ClientError


Endpoint = namedtuple('Endpoint', ['host', 'zone'])

REGION_ENDPOINTS = {
    'us-east-2': Endpoint('s3-website.us-east-2.amazonaws.com', 'Z2O1EMRO9K5GLX'),
    'us-east-1': Endpoint('s3-website-us-east-1.amazonaws.com', 'Z3AQBSTGFYJSTF'),
    'us-west-1': Endpoint('s3-website-us-west-1.amazonaws.com', 'Z2F56UZL2M1ACD'),
    'us-west-2': Endpoint('s3-website-us-west-2.amazonaws.com', 'Z3BJ6K6RIION7M'),
    'ca-central-1': Endpoint('s3-website.ca-central-1.amazonaws.com', 'Z1QDHH18159H29'),
    'ap-south-1': Endpoint('s3-website.ap-south-1.amazonaws.com', 'Z11RGJOFQNVJUP'),
    'ap-northeast-2': Endpoint('s3-website.ap-northeast-2.amazonaws.com', 'Z3W03O7B5YMIYP'),
    'ap-northeast-3': Endpoint('s3-website.ap-northeast-3.amazonaws.com', 'Z2YQB5RD63NC85'),
    'ap-southeast-1': Endpoint('s3-website-ap-southeast-1.amazonaws.com', 'Z3O0J2DXBE1FTB'),
    'ap-southeast-2': Endpoint('s3-website-ap-southeast-2.amazonaws.com', 'Z1WCIGYICN2BYD'),
    'ap-northeast-1': Endpoint('s3-website-ap-northeast-1.amazonaws.com', 'Z2M4EHUR26P7ZW'),
    'cn-northwest-1': Endpoint('s3-website.cn-northwest-1.amazonaws.com.cn', None),
    'eu-central-1': Endpoint('s3-website.eu-central-1.amazonaws.com', 'Z21DNDUVLTQW6Q'),
    'eu-west-1': Endpoint('s3-website-eu-west-1.amazonaws.com', 'Z1BKCTXD74EZPE'),
    'eu-west-2': Endpoint('s3-website.eu-west-2.amazonaws.com', 'Z3GKZC51ZF0DB4'),
    'eu-west-3': Endpoint('s3-website.eu-west-3.amazonaws.com', 'Z3R1K369G5AVDG'),
    'sa-east-1': Endpoint('s3-website-sa-east-1.amazonaws.com', 'Z7KQH4QJS55SO'),
}


def get_endpoint(region):
    """Get the S3 website hosting endpoint for this region."""
    return REGION_ENDPOINTS[region]


def get_bucket_region(session, bucket_name):
    """Get the bucket's region name."""
    try:
        bucket_location = session.resource('s3').meta.client.get_bucket_location(Bucket=bucket_name)
        return bucket_location["LocationConstraint"] or 'us-east-1'

    except ClientError as err:
        print('Unable to find bucket: {0}. '.format(bucket_name) + str(err) + '\n')


def set_bucket_policy(bucket):
    """Configures bucket policy to allow public reads"""
    policy = '''
    {
        "Version":"2012-10-17",
        "Statement":[
            {
                "Sid":"PublicReadGetObject",
                "Effect":"Allow",
                "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::%s/*"]
            }
        ]
    }
    ''' % bucket.name

    policy = policy.strip()

    try:
        print('Applying public read permissions to {0}...'.format(bucket.name))
        return bucket.Policy().put(Policy=policy)

    except ClientError as err:
        print('Unable to apply bucket policy to {0}. '.format(bucket.name) + str(err) + '\n')
        raise err


def set_website_config(bucket):
    """Configures bucket for static site hosting"""
    try:
        print('Applying static site configurations to {0}...'.format(bucket.name))
        return bucket.Website().put(WebsiteConfiguration={
            "ErrorDocument": {
                "Key": "error.html"
            },
            "IndexDocument": {
                "Suffix": "index.html"
            }
        })

    except ClientError as err:
        print('Unable to apply bucket policy to {0}. '.format(bucket.name) + str(err)+ '\n')
        raise err
