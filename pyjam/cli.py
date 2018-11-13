import boto3
import click
from pyjam.client import set_client
from pyjam.utils.bucket import print_objects


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    PyJAM deploys static sites to S3 and configures Route53 and CloudFront

    Append [options] to the end of the command
    """
    pass


"""
***
*** PyJAM list commands
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

    return


@ls.command('bucket')
@click.argument('bucket')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def list_bucket_objects(bucket, **kwargs):
    """List objects in an S3 bucket [options]"""
    s3 = set_client(**kwargs)

    print_objects(s3, bucket)

    return


if __name__ == '__main__':
    cli()