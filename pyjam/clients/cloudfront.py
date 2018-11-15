"""CloudFront Client for PyJam"""

import uuid
import boto3
from botocore.exceptions import ClientError
from pyjam.utils.s3 import get_endpoint


class CloudFrontClient:
    """Class for CloudFront Client"""

    def __init__(self, **kwargs):
        """Create a DistributionManager."""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.cloudfront = self.session.client('cloudfront')
        self.acm = self.session.client('acm', region_name='us-east-1')


    def certificate_matches(self, certificate_arn, domain_name):
        """Return True if cert matches domain_name."""
        cert_details = self.acm.describe_certificate(CertificateArn=certificate_arn)
        alt_names = cert_details['Certificate']['SubjectAlternativeNames']

        for name in alt_names:
            if name == domain_name:
                return True

            if name[0] == '*' and domain_name.endswith(name[1:]):
                return True

        return False


    def find_matching_cert(self, domain_name):
        """Find a certificate matching domain_name."""
        paginator = self.acm.get_paginator('list_certificates')
        for page in paginator.paginate(CertificateStatuses=['ISSUED']):
            for cert in page['CertificateSummaryList']:
                if self.certificate_matches(cert['CertificateArn'], domain_name):
                    return cert

        return None



    def create_distribution(self, domain_name, region, cert):
        """Create a dist for domain_name using cert."""
        origin_id = 'S3-Website-' + domain_name

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
                                '{0}.{1}'.format(domain_name, get_endpoint(region)),
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
