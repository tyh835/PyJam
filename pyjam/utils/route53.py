"""Utilities for Route53"""

import uuid
from botocore.exceptions import ClientError

def find_hosted_zone(client, domain_name):
    """Find a hosted zone matching domain"""
    paginator = client.get_paginator('list_hosted_zones')
    for page in paginator.paginate():
        for zone in page['HostedZones']:
            if domain_name.endswith(zone['Name'][:-1]):
                return zone

    return None


def create_hosted_zone(client, domain_name):
    """Create a hosted zone to match domain"""
    zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
    try:
        return client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4())
        )

    except ClientError as err:
        print('Unable to create hosted zone for {0}. '.format(domain_name) + str(err) + '\n')
