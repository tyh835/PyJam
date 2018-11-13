import boto3
import click
from pydeploy.client import set_client


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    Pydeploy deploys static sites to S3 and configures Route53 and CloudFront

    Append [options] to the end of the command
    """
    pass


"""
***
*** Pydeploy list commands
***
"""

@cli.group('list')
def ls():
    """Command for listing buckets and objects"""
    pass


@ls.command('buckets')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def list_buckets(**kwargs):
    """List all S3 buckets [options]"""
    s3 = set_client(**kwargs)

    for bucket in s3.buckets.all():
        print('s3://' + bucket.name)


@ls.command('objects')
@click.option('--bucket', default=None, help='List objects in the specified S3 bucket.')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def list_bucket_objects(bucket, **kwargs):
    """List objects in an S3 bucket [options]"""
    s3 = set_client(**kwargs)

    if not bucket:
        print('Error: --bucket option is required')
        return

    for obj in s3.Bucket(bucket).objects.all():
        print(obj.key)


if __name__ == '__main__':
    cli()