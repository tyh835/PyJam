import boto3
import click
from pydeploy.client import set_client

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    PyDeploy deploys static sites to S3 and configures Route53 and CloudFront

    Append [options] to the end of the command
    """
    pass

if __name__ == '__main__':
    cli()