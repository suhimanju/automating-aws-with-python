import boto3
from faker import Faker

fake = Faker()

session = boto3.Session(profile_name='pythonAutomation')

s3 = session.resource('s3')

# create bucket
# aws s3 mb s3://suhas-search-engine --profile pythonAutomation

# need location constraint
new_bucket = s3.create_bucket(Bucket='automating-aws-boto3-' + str(
    fake.random_int()), CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
