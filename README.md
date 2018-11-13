# PyDeploy

Version: 0.1.0

## About

`pydeploy` is a CLI tool to deploy static websites by syncing to an S3 bucket, and optionally configure Route53, and CloudFront.

## Configuring

Run `pipenv install` in the file directory.

If you don't yet have `pipenv`, install at [https://pipenv.readthedocs.io/en/latest/](https://pipenv.readthedocs.io/en/latest/)

Use the standard configuration on the AWS CLI. e.g.

`aws configure`

and add your Access and Secret keys.

The profile should be an AWS power user (more restrictive permissions pending).