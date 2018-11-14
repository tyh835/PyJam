from botocore.exceptions import ClientError


def print_objects(s3, bucket_name):
    """
    Arguments:
        s3: s3.ServiceResource -- Instance of S3 ServiceResource
        bucket_name: str -- Name of the S3 bucket to list
    """

    try:
        for obj in s3.Bucket(bucket_name).objects.all():
            print(obj.key)

    except ClientError as err:
        print('Unable to list bucket: {0}. '.format(bucket_name) + str(err))

    return


def setup_hosting_bucket(s3, region, bucket_name):
    """
    Arguments:
        s3: s3.ServiceResource -- Instance of S3 ServiceResource
        region: str -- AWS region in which to setup the bucket
        bucket_name: str -- Name of the S3 bucket to setup
    """

    try:
        bucket = create_bucket(s3, region, bucket_name)
        set_bucket_policy(bucket)
        set_website_config(bucket)
        print('Success!')

    except ClientError as err:
        print('Failed to setup bucket {0}. '.format(bucket_name) + str(err))

    return


def create_bucket(s3, region, bucket_name):
    """
    Arguments:
        s3: s3.ServiceResource -- Instance of S3 ServiceResource
        region: str -- AWS region in which to setup the bucket
        bucket_name: str -- Name of the S3 bucket to create

    Returns:
        s3.Bucket -- Instance of S3 Bucket just created
    """

    try:
        if region == 'us-east-1':
            print('\nCreating S3 bucket {0}.'.format(bucket_name))
            return s3.create_bucket(Bucket=bucket_name)
        else:
            print('\nCreating S3 bucket {0}.'.format(bucket_name))
            return s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )

    except ClientError as err:
        if err.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(' {0} already exists. Continuing...'.format(bucket_name))
            return s3.Bucket(bucket_name)

        else:
            print(' Unable to create bucket: {0}. '.format(bucket_name) + str(err))
            raise(err)


def set_bucket_policy(bucket):
    """
    Arguments:
        bucket: s3.Bucket -- Instance of S3 Bucket

    Returns:
        Response -- HTTP Response of setting bucket policy
    """

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
        print(' Applying public read permissions to {0}...'.format(bucket.name))
        return bucket.Policy().put(Policy=policy)

    except ClientError as err:
        print(' Unable to apply bucket policy to {0}. '.format(bucket.name) + str(err))
        raise err


def set_website_config(bucket):
    """
    Arguments:
        bucket: s3.Bucket -- Instance of S3 Bucket

    Returns:
        Response -- HTTP Response of setting website configuration
    """
    try:
        print(' Applying static site configurations to {0}...'.format(bucket.name))
        return bucket.Website().put(WebsiteConfiguration={
            "ErrorDocument": {
                "Key": "error.html"
            },
            "IndexDocument": {
                "Suffix": "index.html"
            }
        })

    except ClientError as err:
        print(' Unable to apply bucket policy to {0}. '.format(bucket.name) + str(err))
        raise err