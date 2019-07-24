import boto3
import click

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

if __name__ == '__main__':
    cli()