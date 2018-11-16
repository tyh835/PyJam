# PyJam

Version: 0.2.1

## About

`jam` is a CLI tool to deploy static sites to AWS. It can sync to an S3 bucket, and configuring it for static site hosting. It can also optionally configure Route53 and CloudFront.

Serving static site with rich functionalities from a CDN is the basis of the JAM stack. Find out more about the JAM stack here: [https://jamstack.org/](https://jamstack.org/)

This project is based on [acloud.guru](acloud.guru)'s course Automating AWS with Python's project. Improvements include error handling, API, deleting stale files on sync, and configuring CloudFront to directly cache S3 website hosting URL.

## Configuring for Development

Run `pipenv install` in the file directory.

If you don't yet have `pipenv`, install at [https://pipenv.readthedocs.io/en/latest/](https://pipenv.readthedocs.io/en/latest/)

Use the standard configuration on the AWS CLI. e.g. `aws configure` and add your Access and Secret keys.

The profile should be an AWS power user (more restrictive permissions pending).

## Commands

`jam list buckets` - Lists all S3 buckets

`jam list bucket <name>` - Lists all objects in an S3 bucket

`jam setup bucket <name>` - Create and configure an S3 bucket for static site hosting. Only configures the bucket if it already exists.

- `--region` specifies the AWS region to setup the S3 bucket.

`jam setup domain <name>` - Create and configure a Route53 domain records for S3 or CloudFront.

- `--s3`: create records to point to S3 hosted website with corresponding domain name. NOTE: bucket name must be the same as domain name.

- `--cf`: create records to point a CloudFront distribution. NOTE: distribution CNAME must point to the domain name.

`jam setup cloudfront` - Create and configure a CloudFront distribution to cache a S3 hosted static website.

`jam sync <path-name> <bucket-name>` - Sync file directory recursively to S3 bucket. Removes stale files and checks for unnecessary uploads.

## Options

`--profile` specifies the AWS profile to use as credentials.

## Installation

You can build from source by cloning the this git repository:

`git clone https://github.com/tyh835/pyjam.git`

and build by running `cd pyjam && pipenv install` and `pipenv run python setup.py bdist_wheel`.

Then, install the package using `pip3 install dist/<wheel-file-name-here>.whl`

Or, you can install the package directly at:

`pip3 install https://s3-us-west-2.amazonaws.com/tyh835-bin/pyjam-0.2.1-py3-none-any`

Then, run `jam --help` and you are all set!