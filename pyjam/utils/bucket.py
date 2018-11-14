from botocore.exceptions import ClientError


def print_objects(s3, bucket):
    try:
        for obj in s3.Bucket(bucket).objects.all():
            print(obj.key)

    except ClientError as err:
        print('Unable to list bucket: {0}. '.format(bucket) + str(err))

    return


def create_bucket(s3, region, bucket_name):
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
            print('Unable to create bucket: {0}. '.format(bucket_name) + str(err))
            raise(err)


def set_bucket_policy(bucket):
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
        print('Unable to apply bucket policy to {0}. '.format(bucket.name) + str(err))
        raise err


def set_website_config(bucket):

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
        print('Unable to apply bucket policy to {0}. '.format(bucket.name) + str(err))
        raise err