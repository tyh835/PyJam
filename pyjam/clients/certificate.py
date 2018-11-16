"""ACM Client for PyJam"""

from time import sleep
import boto3
from botocore.exceptions import ClientError
from pyjam.utils.route53 import find_hosted_zone, create_hosted_zone


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


    def create_validation_record(self, domain_name, certificate):
        """Create a CNAME record for domain certificate validation"""
        if domain_name[0] == '*':
            domain_name = domain_name[2:]

        try:
            zone = find_hosted_zone(self.route53, domain_name) \
            or create_hosted_zone(self.route53, domain_name)
            validation_records = certificate['DomainValidationOptions']

            print('Creating CNAME record for DNS validation...')

            for record in validation_records:
                try:
                    resource_record = record['ResourceRecord']

                    self.route53.change_resource_record_sets(
                        HostedZoneId=zone['Id'],
                        ChangeBatch={
                            'Comment': 'Created by PyJam',
                            'Changes': [
                                {
                                    'Action': 'UPSERT',
                                    'ResourceRecordSet': {
                                        'Name': resource_record['Name'],
                                        'Type': resource_record['Type'],
                                        'TTL': 60,
                                        'ResourceRecords': [
                                            {
                                                'Value': resource_record['Value']
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    )

                    return True

                except KeyError:
                    print('AWS did not return a valid response. please try again in 5 seconds.')
                    return False

        except ClientError as err:
            print('Unable to create CNAME record for validation of domain {0}. '.format(
                domain_name
            ) + str(err) + '\n')


    def request_certificate(self, domain_name):
        """Requests an ACM SSL certificate for your domain"""
        try:
            alt_name = '*.' + domain_name if domain_name[0] != '*' else domain_name[2:]

            print('Requesting certificate for domain {0}...'.format(domain_name))

            response = self.acm.request_certificate(
                DomainName=domain_name,
                ValidationMethod='DNS',
                SubjectAlternativeNames=[
                    alt_name,
                ]
            )

            certificate_arn = response['CertificateArn']
            sleep(6)
            certificate = self.describe_certificate(certificate_arn)['Certificate']
            success = self.create_validation_record(domain_name, certificate)

            if success:
                self.await_validation(certificate_arn)

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

        print('\nSuccess!')
