"""CloudFront Client for PyJam"""

import uuid
import boto3
from botocore.exceptions import ClientError


class CloudFrontClient:
    """Class for CloudFront Client"""

    def __init__(self, **kwargs):
        """Create a DistributionManager."""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.cloudfront = self.session.client('cloudfront')


    def find_matching_distribution(self, domain_name):
        """Find a dist matching domain_name."""
        paginator = self.cloudfront.get_paginator('list_distributions')
        for page in paginator.paginate():
            print(page)
            for dist in page['DistributionList'].get('Items', []):
                for alias in dist['Aliases']['Items']:
                    if alias == domain_name:
                        return dist

        return None


    def create_distribution(self, domain_name, region, cert):
        """Create a dist for domain_name using cert."""
        origin_id = 'S3-Website-' + domain_name
        region_name = '-' + region

        if region == 'us-east-1':
            region_name = ''

        try:
            result = self.cloudfront.create_distribution(
                DistributionConfig={
                    'CallerReference': str(uuid.uuid4()),
                    'Aliases': {
                        'Quantity': 1,
                        'Items': [domain_name]
                    },
                    'DefaultRootObject': 'index.html',
                    'Comment': 'Created by PyJam',
                    'Enabled': True,
                    'Origins': {
                        'Quantity': 1,
                        'Items': [
                            {
                                'Id': origin_id,
                                'DomainName':
                                '{0}.s3-website{1}.amazonaws.com'.format(domain_name, region_name),
                                'S3OriginConfig': {
                                    'OriginAccessIdentity': ''
                                }
                            }
                        ]
                    },
                    'DefaultCacheBehavior': {
                        'TargetOriginId': origin_id,
                        'ViewerProtocolPolicy': 'redirect-to-https',
                        'TrustedSigners': {
                            'Quantity': 0,
                            'Enabled': False
                        },
                        'ForwardedValues': {
                            'Cookies': {'Forward': 'all'},
                            'Headers': {'Quantity': 0},
                            'QueryString': False,
                            'QueryStringCacheKeys': {'Quantity': 0}
                        },
                        'DefaultTTL': 86400,
                        'MinTTL': 3600
                    },
                    'ViewerCertificate': {
                        'ACMCertificateArn': cert['CertificateArn'],
                        'SSLSupportMethod': 'sni-only',
                        'MinimumProtocolVersion': 'TLSv1.1_2016'
                    }
                }
            )

            return result['Distribution']

        except ClientError as err:
            print('Unable to create distribution for {0}. '.format(domain_name) + str(err) + '\n')




    def await_deploy(self, dist):
        """Wait for dist to be deployed."""
        waiter = self.cloudfront.get_waiter('distribution_deployed')
        waiter.wait(Id=dist['Id'], WaiterConfig={
            'Delay': 30,
            'MaxAttempts': 50
        })
