"""CLI entrypoint for PyJam"""

import click
from pyjam.constants import VERSION
from pyjam.clients import S3Client, Route53Client

@click.group()
@click.version_option(version=VERSION)
def cli():
    """
    PyJam deploys static sites to S3 and configures Route53 and CloudFront

    Append [options] to the end of the command
    """
    pass

###
### PyJam list commands
###


@cli.group('list')
def lst():
    """Command for listing S3 buckets and objects"""
    pass


@lst.command('buckets')
@click.option('--profile', 'profile_name', default=None, help='Specify the AWS profile \
to use as credentials.')
def list_buckets(**kwargs):
    """Lists all S3 buckets [options]"""
    client = S3Client(**kwargs)
    return client.print_buckets()


@lst.command('bucket')
@click.argument('bucket_name')
@click.option('--profile', 'profile_name', default=None, help='Specify the AWS profile \
to use as credentials.')
def list_bucket_objects(bucket_name, **kwargs):
    """Lists objects in an S3 bucket [options]"""
    client = S3Client(**kwargs)
    return client.print_objects(bucket_name)


###
### PyJam sync command
###

@cli.command('sync')
@click.argument('path', type=click.Path(exists=True))
@click.argument('bucket')
@click.option('--profile', 'profile_name', default=None, help='Specify the AWS profile \
to use as credentials.')
def sync(path, bucket, **kwargs):
    """Command for syncing contents of PATH recursively to S3 BUCKET"""
    client = S3Client(**kwargs)
    return client.sync_to_bucket(path, bucket)

###
### PyJam setup commands
###


@cli.group('setup')
def setup():
    """Command for setting up S3 buckets, Route53, and CloudFront"""
    pass


@setup.command('bucket')
@click.argument('bucket_name')
@click.option('--region', 'region_name', default=None, help='Specify the AWS region \
to create the bucket.')
@click.option('--profile', 'profile_name', default=None, help='Specify the AWS profile \
to use as credentials.')
def setup_bucket(bucket_name, **kwargs):
    """Setup S3 bucket for website hosting [options]"""
    client = S3Client(**kwargs)
    return client.setup_hosting_bucket(bucket_name)


@setup.command('domain')
@click.argument('domain')
@click.option('--s3', is_flag=True, default=False, help='Setup domain record for S3 bucket')
@click.option('--cf', is_flag=True, default=False, help='Setup domain record for CloudFront')
@click.option('--profile', 'profile_name', default=None, help='Specify the AWS profile \
to use as credentials.')
def setup_domain(domain, s3, cf, **kwargs):
    """Setup S3 bucket for website hosting [options]"""
    client = Route53Client(**kwargs)
    if not s3 and not cf:
        print('Error: please specify an option (--s3 or --cf)')
    if s3:
        client.create_s3_domain_record(domain)
    if cf:
        client.create_cf_domain_record(domain)


if __name__ == '__main__':
    cli()
