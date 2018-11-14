import click
from pyjam.constants import version
from pyjam.clients import set_s3client
from pyjam.utils.bucket import (
    print_objects,
    setup_hosting_bucket,
    sync_to_bucket
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
@click.argument('bucket_name')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def list_bucket_objects(bucket_name, **kwargs):
    """List objects in an S3 bucket [options]"""
    s3, _ = set_s3client(**kwargs)

    return print_objects(s3, bucket_name)


"""
***
*** PyJam sync command
***
"""

@cli.command('sync')
@click.argument('path', type=click.Path(exists=True))
@click.argument('bucket_name')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def sync(path, bucket_name, **kwargs):
    """Sync contents of PATHNAME to BUCKET"""
    s3, _ = set_s3client(**kwargs)

    sync_to_bucket(s3, bucket_name, path)

    return



"""
***
*** PyJam setup commands
***
"""

@cli.group('setup')
def setup():
    """Command for setting up S3 buckets, Route53, and CloudFront"""
    pass


@setup.command('bucket')
@click.argument('bucket_name')
@click.option('--region', default=None, help='Specify the AWS region to create the bucket.')
@click.option('--profile', default=None, help='Specify the AWS profile to use as credentials.')
def setup_bucket(bucket_name, **kwargs):
    """Setup S3 bucket for website hosting [options]"""
    s3, session = set_s3client(**kwargs)
    region = session.region_name

    return setup_hosting_bucket(s3, region, bucket_name)


if __name__ == '__main__':
    cli()