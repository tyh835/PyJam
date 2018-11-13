# PyJAM

Version: 0.1.1

## About

`pyjam` is a CLI tool to deploy static websites by syncing to an S3 bucket, and optionally configure Route53, and CloudFront.

Serving static site with rich functionalities from a CDN is the basis of the JAM stack. Find out more about the JAM stack here: [https://jamstack.org/](https://jamstack.org/)

## Configuring for Development

Run `pipenv install` in the file directory.

If you don't yet have `pipenv`, install at [https://pipenv.readthedocs.io/en/latest/](https://pipenv.readthedocs.io/en/latest/)

Use the standard configuration on the AWS CLI. e.g.

`aws configure`

and add your Access and Secret keys.

The profile should be an AWS power user (more restrictive permissions pending).

## Commands

`jam list buckets` - Lists all S3 buckets

`jam list bucket <name>` - Lists all objects in an S3 bucket