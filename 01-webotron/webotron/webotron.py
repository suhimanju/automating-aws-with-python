#!/usr/bin/python

"""
Webotron: Deploy websites with aws.

Webotron automates the process of deploying the static websites to AWS.

- Configure AWS S3 buckets
    - Create buckets
    - Set them up for static website hosting
    - Deploy local files to buckets
- Configure DNS with AWS Route 53
- Configure a Content Delivery Network and SSL with AWS Cloudfront
"""

import mimetypes
from pathlib import Path

import click

import boto3
from botocore.errorfactory import ClientError

session = boto3.Session(profile_name='pythonAutomation')

s3 = session.resource('s3')


@click.group()
def cli():
    """Webotron deploys websites to AWS."""
    pass


@cli.command('list-buckets')
def list_buckets():
    """List buckets contained in the aws profile \n
    aws s3 ls --profile pythonAutomation."""
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects within the bucket."""
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure S3 bucket."""
    s3_bucket = None

    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': session.region_name}
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise error

    policy = """{
        "Version": "2008-10-17",
        "Statement": [
                {
                "Sid": "AllowPublicRead",
                "Effect": "Allow",
                "Principal": {
                        "AWS": "*"
                },
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::%s/*"
                }
        ]
        }""" % s3_bucket.name

    policy = policy.strip()
    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    s3_bucket.Website().put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }})

    return


def upload_file(s3_bucket, path, key):
    """Upload a directory content in the local to s3_bucket, with each filename being the key."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'

    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    "Sync contents to PATHNAME to Bucket"
    s3_bucket = s3.Bucket(bucket)
    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(Path(root))


if __name__ == '__main__':
    cli()
