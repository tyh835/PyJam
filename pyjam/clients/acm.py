"""ACM Certificate Client for PyJam"""

import boto3


class ACMClient:
    """Class for ACM Certificate Client"""

    def __init__(self, **kwargs):
        """Create a CertificateManager."""
        params = {k:v for k, v in kwargs.items() if v is not None}

        self.session = boto3.Session(**params)
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
