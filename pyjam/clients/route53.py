"""Route53 Client for PyJam"""

import boto3
from botocore.exceptions import ClientError
from pyjam.utils.s3 import set_bucket_policy, set_website_config, get_endpoint, get_bucket_region
from pyjam.utils.route53 import find_hosted_zone, create_hosted_zone

class Route53Client:
    """Class for Route53 Client"""

    def __init__(self, **kwargs):
        """Setup Route53 Client Configurations"""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.route53 = self.session.client('route53')
        self.s3 = self.session.resource('s3')
        self.cloudfront = self.session.client('cloudfront')


    def find_matching_bucket(self, domain_name):
        """Find a S3 bucket with matching domain"""
        try:
            bucket = self.s3.Bucket(domain_name)
            print('\nFound bucket s3://{0}'.format(domain_name))
            set_bucket_policy(bucket)
            set_website_config(bucket)

        except ClientError as err:
            print('Unable to find bucket {0}. '.format(domain_name) + str(err) + '\n')
            print('Please run `jam setup bucket {0}` first. '.format(domain_name))

            raise err


    def find_matching_distribution(self, domain_name):
        """Find a CloudFront distribution with matching domain"""
        paginator = self.cloudfront.get_paginator('list_distributions')
        for page in paginator.paginate():
            for distribution in page['DistributionList'].get('Items', []):
                for alias in distribution['Aliases']['Items']:
                    if alias == domain_name:
                        return distribution

        return {}


    def create_s3_domain_record(self, domain_name):
        """Create a domain record in hosted zone for S3 Hosting"""

        try:
            self.find_matching_bucket(domain_name)
            region = get_bucket_region(self.session, domain_name)
            zone = find_hosted_zone(self.route53, domain_name) \
            or create_hosted_zone(self.route53, domain_name)
            endpoint = get_endpoint(region)

            print('Creating Alias record for {0}...'.format(domain_name))

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

            print('\nDomain configured: http://{0}'.format(domain_name))

        except ClientError as err:
            print('\nUnable to create Alias record to point to {0}. '.format(
                domain_name + '.' + endpoint.host
            ) + str(err) + '\n')



    def create_cf_domain_record(self, domain_name):
        """Create a domain record in hosted zone for CloudFront"""
        try:
            zone = find_hosted_zone(self.route53, domain_name) \
            or create_hosted_zone(self.route53, domain_name)
            cf_domain = self.find_matching_distribution(domain_name).get('DomainName', None)

            if not cf_domain:
                print('\nError: matching CloudFront distribution does not exist.')
                print('Please run `jam setup distribution` first.\n')
                return

            print('Creating Alias record for {0}...'.format(domain_name))

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
                                    'HostedZoneId': 'Z2FDTNDATAQYW2',
                                    'DNSName': cf_domain,
                                    'EvaluateTargetHealth': False
                                }
                            }
                        }
                    ]
                }
            )

            self.route53.change_resource_record_sets(
                HostedZoneId=zone['Id'],
                ChangeBatch={
                    'Comment': 'Created by PyJam',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'AAAA',
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

            print('\nDomain configured: https://{0}'.format(domain_name))

        except ClientError as err:
            print('Unable to create Alias record for {0}. '.format(
                domain_name
            ) + str(err) + '\n')
