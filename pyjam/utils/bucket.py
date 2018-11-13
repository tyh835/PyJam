from botocore.exceptions import ClientError

def print_objects(s3, bucket):
    try:
        for obj in s3.Bucket(bucket).objects.all():
            print(obj.key)

    except ClientError as err:
        print('Unable to list bucket: {0}. '.format(bucket) + str(err))

    return


def create_bucket(s3, session, bucket):
    try:
        if session.region_name == 'us-east-1':
            s3_bucket = s3.create_bucket(Bucket=bucket)
        else:
            s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={'LocationConstraint': session.region_name})

        return s3_bucket

    except ClientError as err:
        if err.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)

            return s3_bucket
        else:
            raise err