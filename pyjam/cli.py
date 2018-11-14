import click
from pyjam.constants import version
from pyjam.client import set_s3client
from pyjam.utils.bucket import (
    print_objects,
    create_bucket,
    set_bucket_policy,
    set_website_config
)


@click.group()
@click.version_option(version=version)
def cli():
    """
    PyJam deploys static sites to S3 and configures Route53 and CloudFront

    Append [options] to the end of the command
    """
    pass


"""
***
*** PyJam list commands
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
    s3, _ = set_s3client(**kwargs)

    for bucket in s3.buckets.all():
        print('s3://' + bucket.name)

    return


@ls.command('bucket')
@click.argument('name', 'bucket_name')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def list_bucket_objects(bucket_name, **kwargs):
    """List objects in an S3 bucket <NAME> [options]"""
    s3, _ = set_s3client(**kwargs)

    print_objects(s3, bucket_name)

    return


"""
***
*** PyJam list commands
***
"""

@cli.group('setup')
def setup():
    """Command for setting up S3 buckets, Route53, and CloudFront"""
    pass


@setup.command('bucket')
@click.argument('name', 'bucket_name')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def setup_bucket(bucket_name, **kwargs):
    s3, session = set_s3client(**kwargs)
    region = session.region_name

    bucket = create_bucket(s3, region, bucket_name)
    set_bucket_policy(bucket)
    set_website_config(bucket)

    print('Success!')
    return


if __name__ == '__main__':
    cli()