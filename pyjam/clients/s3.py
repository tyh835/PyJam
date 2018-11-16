"""S3 Client for PyJam"""

import mimetypes
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

from pyjam.utils.s3 import set_bucket_policy, set_website_config, get_endpoint, get_bucket_region
from pyjam.utils.checksum import generate_checksum
from pyjam.constants import CHUNK_SIZE


class S3Client:
    """Class for S3 Client"""

    def __init__(self, **kwargs):
        """Setup S3 Client Configurations"""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.s3 = self.session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=CHUNK_SIZE,
            multipart_threshold=CHUNK_SIZE
        )
        self.checksums = {}
        self.new_checksums = {}


    def get_bucket_endpoint(self, bucket_name):
        """Get the S3 endpoints for this bucket."""
        return get_endpoint(get_bucket_region(self.session, bucket_name))


    def get_bucket_url(self, bucket_name):
        """Get the website URL for this bucket."""
        return "http://{}.{}".format(
            bucket_name,
            get_endpoint(get_bucket_region(self.session, bucket_name)).host
        )


    def load_checksums(self, bucket_name):
        """Load etag metadata for caching purposes."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                self.checksums[obj['Key']] = obj['ETag']


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
            print('\nFailed to setup bucket: {0}. '.format(bucket_name))


    def sync_to_bucket(self, path, bucket_name):
        """Sync path recursively to the given bucket"""
        self.load_checksums(bucket_name)
        bucket = self.s3.Bucket(bucket_name)
        root_path = Path(path).expanduser().resolve()


        def recursive_upload(bucket, target_path):
            """Uploads files recursively from root path to S3 bucket"""
            for path in target_path.iterdir():
                if path.is_dir():
                    recursive_upload(bucket, path)


                if path.is_file():
                    key = str(path.relative_to(root_path))
                    path = str(path)

                    etag = self.upload_file(bucket, path, key)

                    self.new_checksums[key] = etag

        try:
            print('\nBegin syncing {0} to bucket {1}...\n'.format(path, bucket_name))
            recursive_upload(bucket, root_path)
            self.delete_objects(bucket)
            print('\nSuccess!')

        except ClientError:
            print('\nUnable to sync path: {0} to bucket: {1}. '.format(path, bucket_name))


    def upload_file(self, bucket, path, key):
        """Uploads file to S3 bucket"""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        checksum = generate_checksum(path)

        if self.checksums.get(key, '') == checksum:
            print('Skipping {0}... checksums match'.format(key))
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
                Config=self.transfer_config
            )

            return checksum

        except ClientError as err:
            print('Unable to upload file: {0} to {1}. '.format(path, bucket.name) + str(err))
            raise err


    def delete_objects(self, bucket):
        """Deletes obsolete objects in bucket based on checksum"""
        try:
            for obj in bucket.objects.all():
                key = obj.key

                if self.checksums.get(key, '') and not self.new_checksums.get(key, ''):
                    print('Deleting {0} from {1}.'.format(key, bucket.name))
                    obj.delete()

        except ClientError as err:
            print('Unable to delete object in {0}. '.format(bucket.name) + str(err) + '\n')
