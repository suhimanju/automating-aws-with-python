import boto3
import click

from botocore.errorfactory import ClientError

session = boto3.Session(profile_name='pythonAutomation')

s3 = session.resource('s3')


@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass


@cli.command('list-buckets')
def list_buckets():
    """List buckets contained in the aws profile \n
    aws s3 ls --profile pythonAutomation"""
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List objects within the bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and configure S3 bucket"
    s3_bucket = None

    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': session.region_name}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e

    print(s3_bucket) 
       
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

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }}
    )


if __name__ == '__main__':
    cli()
