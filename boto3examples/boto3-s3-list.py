import boto3

session = boto3.Session(profile_name='pythonAutomation')

s3 = session.resource('s3')

# list buckets contained in the aws profile
# aws s3 ls --profile pythonAutomation

for bucket in s3.buckets.all():
    print(bucket)