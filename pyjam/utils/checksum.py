"""Utilities for generating checksums for S3 objects"""

from hashlib import md5
from functools import reduce
from pyjam.constants import CHUNK_SIZE


def hash_data(data):
    """Generate md5 hash for data."""
    data_hash = md5()
    data_hash.update(data)

    return data_hash


def generate_checksum(path):
    """Generate checksum (S3 ETag) for file based on path"""
    hashes = []

    with open(path, 'rb') as file:
        while True:
            data = file.read(CHUNK_SIZE)

            if not data:
                break

            hashes.append(hash_data(data))

    if not hashes:
        return '""'

    if len(hashes) == 1:
        return '"{0}"'.format(hashes[0].hexdigest())

    digests = (h.digest() for h in hashes)
    data_hash = hash_data(reduce(lambda x, y: x + y, digests))
    return '"{0}-{1}"'.format(data_hash.hexdigest(), len(hashes))
