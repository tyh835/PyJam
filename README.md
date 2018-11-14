# PyJam

Version: 0.1.5

## About

`pyjam` is a CLI tool to deploy static sute by uploading to an S3 bucket, and configuring it to host a static website. It can also optionally configure Route53 and CloudFront.

Serving static site with rich functionalities from a CDN is the basis of the JAM stack. Find out more about the JAM stack here: [https://jamstack.org/](https://jamstack.org/)

## Configuring for Development

Run `pipenv install` in the file directory.

If you don't yet have `pipenv`, install at [https://pipenv.readthedocs.io/en/latest/](https://pipenv.readthedocs.io/en/latest/)

Use the standard configuration on the AWS CLI. e.g. `aws configure` and add your Access and Secret keys.

The profile should be an AWS power user (more restrictive permissions pending).

## Commands

`jam list buckets` - Lists all S3 buckets

`jam list bucket <name>` - Lists all objects in an S3 bucket

`jam setup bucket <name>` - Create and configure an S3 bucket for static site hosting. Configures the bucket if it already exists.

`jam sync <path-name> <bucket-name>` - Sync file directory recursively to S3 bucket. Removes previous files.

## Installation

You can build from source by cloning the this git repository:

`git clone https://github.com/tyh835/pyjam.git`

and build by running `cd pyjam && pipenv install` and `pipenv run python setup.py bdist_wheel`.

Then, install the binary using `pip3 install dist/<wheel-file-name-here>.whl`

Or, you can install the binary directly at:

`pip3 install https://s3-us-west-2.amazonaws.com/tyh835-bin/pyjam-0.1.5-py3-none-any`

Then, run `jam --help` and you are set!