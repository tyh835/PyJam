"""ACM Client for PyJam"""

import uuid
import boto3
from botocore.exceptions import ClientError
from pyjam.clients import Route53Client

class ACMClient:
    """Class for ACM Client"""

    def __init__(self, **kwargs):
        """Create a DistributionManager."""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
        self.acm = self.session.client('acm', region_name='us-east-1')
        self.route53 = self.session.client('route53')


    def describe_certificate(self, certificate_arn):
        """Describes an ACM certificate based on ARN"""
        try:
            response = self.acm.describe_certificate(
                CertificateArn=certificate_arn
            )
            return response

        except ClientError as err:
            print('Unable to find certificate {0}. '.format(certificate_arn) + str(err) + '\n')


    def find_hosted_zone(self, domain_name):
        """Find a hosted zone matching domain"""
        paginator = self.route53.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None


    def create_hosted_zone(self, domain_name):
        """Create a hosted zone to match domain"""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        try:
            return self.route53.create_hosted_zone(
                Name=zone_name,
                CallerReference=str(uuid.uuid4())
            )

        except ClientError as err:
            print('Unable to create hosted zone for {0}. '.format(domain_name) + str(err) + '\n')


    def create_cname_record(self, certificate):
        """Create a CNAME record for domain certificate validation"""



    def request_certificate(self, domain_name):
        """Requests an ACM SSL certificate for your domain"""
        try:
            alt_name = '*.' + domain_name

            if domain_name and domain_name[0] == '*':
                alt_name = domain_name[2:]

            response = self.acm.request_certificate(
                DomainName=domain_name,
                ValidationMethod='DNS',
                SubjectAlternativeNames=[
                    alt_name,
                ],
                IdempotencyToken=str(uuid.uuid4())
            )

            certificate = self.describe_certificate(response['CertificateArn'])

            self.create_cname_record(certificate)

            self.await_validation(response)

        except ClientError as err:
            print('Unable to request certificate for {0}. '.format(domain_name) + str(err) + '\n')


    def await_validation(self, certificate_arn):
        """Wait for certificate to be validated"""
        waiter = self.acm.get_waiter('certificate_validated')

        print('Awaiting Certificate validation...')
        print('This may take some time.')

        waiter.wait(
            CertificateArn=certificate_arn,
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 80
            }
        )
