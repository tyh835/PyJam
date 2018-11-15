"""S3 Client for PyJam"""

import mimetypes
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

from pyjam.utils.s3 import get_endpoint, set_bucket_policy, set_website_config
from pyjam.utils.checksum import generate_checksum
from pyjam.constants import CHUNK_SIZE


class S3Client:
    """Class for S3 Client"""
    def __init__(self, **kwargs):
        """Setup session and s3 ServiceResource"""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.s3 = self.session.resource('s3')
        self.checksums = {}


    def get_bucket(self, bucket_name):
        """Get a bucket by name."""
        return self.s3.Bucket(bucket_name)


    def get_bucket_region(self, bucket_name):
        """Get the bucket's region name."""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket_name)
        return bucket_location["LocationConstraint"] or 'us-east-1'


    def get_bucket_endpoint(self, bucket_name):
        """Get the S3 endpoints for this bucket."""
        return get_endpoint(self.get_bucket_region(bucket_name))


    def get_bucket_url(self, bucket_name):
        """Get the website URL for this bucket."""
        return "http://{}.{}".format(
            bucket_name,
            get_endpoint(self.get_bucket_region(bucket_name)).host
        )


    def load_checksums(self, bucket_name):
        """Load etag metadata for caching purposes."""
        checksums = {}

        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                checksums[obj['Key']] = obj['ETag']

        return checksums


    def create_bucket(self, bucket_name):
        """Creates new S3 bucket in given region"""
        try:
            if self.session.region_name == 'us-east-1':
                print('\nCreating S3 bucket {0}.\n'.format(bucket_name))
                return self.s3.create_bucket(Bucket=bucket_name)

            print('\nCreating S3 bucket {0}.\n'.format(bucket_name))
            return self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.session.region_name
                }
            )

        except ClientError as err:
            if err.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print('{0} already exists. Continuing...'.format(bucket_name))
                return self.s3.Bucket(bucket_name)

            print('Unable to create bucket: {0}.'.format(bucket_name) + str(err))
            raise err


    def print_buckets(self):
        """Lists all S3 buckets"""
        for bucket in self.s3.buckets.all():
            print('s3://' + bucket.name)



    def print_objects(self, bucket_name):
        """Lists all objects in the given bucket"""
        try:
            for obj in self.s3.Bucket(bucket_name).objects.all():
                print(obj.key)

        except ClientError as err:
            print('Unable to list bucket: {0}. '.format(bucket_name) + str(err) + '\n')


    def setup_hosting_bucket(self, bucket_name):
        """Setup S3 bucket for website hosting"""
        try:
            bucket = self.create_bucket(bucket_name)
            set_bucket_policy(bucket)
            set_website_config(bucket)
            print('\nSuccess! URL: {0}'.format(self.get_bucket_url(bucket_name)))

        except ClientError:
            print('\nFailed to setup bucket {0}. '.format(bucket_name))


    def sync_to_bucket(self, path, bucket_name):
        """Sync path recursively to the given bucket"""
        self.checksums = self.load_checksums(bucket_name)
        bucket = self.s3.Bucket(bucket_name)
        root_path = Path(path).expanduser().resolve()
        transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=CHUNK_SIZE,
            multipart_threshold=CHUNK_SIZE
        )

        new_checksums = {}

        def recursive_upload(bucket, target_path):
            """Uploads files recursively from root path to S3 bucket"""
            for path in target_path.iterdir():
                if path.is_dir():
                    recursive_upload(bucket, path)


                if path.is_file():
                    key = str(path.relative_to(root_path))
                    path = str(path)

                    etag = self.upload_file(
                        bucket,
                        path,
                        key,
                        transfer_config
                    )

                    new_checksums[key] = etag

        try:
            print('\nBegin syncing {0} to bucket {1}...'.format(path, bucket_name))
            recursive_upload(bucket, root_path)
            self.delete_objects(bucket, new_checksums)
            print('\nSuccess!')

        except ClientError:
            print('\nFailed to sync path: {0} to bucket: {1}. '.format(path, bucket_name))


    def upload_file(self, bucket, path, key, transfer_config):
        """Uploads file to S3 bucket"""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        checksum = generate_checksum(path)

        if self.checksums.get(key, '') == checksum:
            return checksum

        try:
            print('Uploading {0} to {1} (content-type: {2}).'.format(
                key,
                bucket.name,
                content_type
            ))
            bucket.upload_file(
                path,
                key,
                ExtraArgs={
                    'ContentType': content_type
                },
                Config=transfer_config
            )

            return checksum

        except ClientError as err:
            print('Unable to upload file: {0} to {1}. '.format(path, bucket.name) + str(err))
            raise err


    def delete_objects(self, bucket, new_checksums):
        """Deletes obsolete objects in bucket based on checksum"""
        try:
            for obj in bucket.objects.all():
                key = obj.key

                if self.checksums.get(key, '') and not new_checksums.get(key, ''):
                    print('Deleting {0} from {1}.'.format(key, bucket.name))
                    obj.delete()

        except ClientError as err:
            print('Unable to delete object in {0}. '.format(bucket.name) + str(err) + '\n')
