"""Route53 Client for PyJam"""

import uuid
import boto3
from botocore.exceptions import ClientError

from pyjam.utils.s3 import set_bucket_policy, set_website_config


class Route53Client:
    """Class for Route53 Client"""

    def __init__(self, **kwargs):
        """Setup Route53 Client Configurations"""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.route53 = self.session.client('route53')
        self.s3 = self.session.resource('s3')


    def find_hosted_zone(self, domain_name):
        """Find zone matching domain_name."""
        paginator = self.route53.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None


    def create_hosted_zone(self, domain_name):
        """Create a hosted zone to match domain_name."""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        return self.route53.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4())
        )


    def create_s3_domain_record(self, zone, domain_name, endpoint):
        """Create a domain record in zone for domain_name."""
        try:
            bucket = self.s3.Bucket(domain_name)
            print('\nFound bucket s3://{0}'.format(domain_name))
            set_bucket_policy(bucket)
            set_website_config(bucket)

        except ClientError as err:
            print('Unable to find bucket {0}. Please first setup hosting S3 bucket. '.format(
                domain_name
            ) + str(err) + '\n')
            return

        try:
            self.route53.change_resource_record_sets(
                HostedZoneId=zone['Id'],
                ChangeBatch={
                    'Comment': 'Created by PyJam',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'A',
                                'AliasTarget': {
                                    'HostedZoneId': endpoint.zone,
                                    'DNSName': endpoint.host,
                                    'EvaluateTargetHealth': False
                                }
                            }
                        }
                    ]
                }
            )

        except ClientError as err:
            print('Unable to create Alias record for {0} to point to {1}. '.format(
                domain_name,
                domain_name + '.' + endpoint.host
            ) + str(err) + '\n')



    def create_cf_domain_record(self, zone, domain_name, cf_domain):
        """Create a domain record in zone for domain_name."""
        try:
            self.route53.change_resource_record_sets(
                HostedZoneId=zone['Id'],
                ChangeBatch={
                    'Comment': 'Created by webotron',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'A',
                                'AliasTarget': {
                                    'HostedZoneId': 'Z2FDTNDATAQYW2',
                                    'DNSName': cf_domain,
                                    'EvaluateTargetHealth': False
                                }
                            }
                        }
                    ]
                }
            )

        except ClientError as err:
            print('Unable to create Alias record for {0} to point to {1}. '.format(
                domain_name,
                cf_domain
            ) + str(err) + '\n')
