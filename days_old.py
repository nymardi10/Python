import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
ses = boto3.client('ses')
from botocore.exceptions import ClientError

EMAIL_FROM = 'nymardi@gmail.com'
EMAIL_TO   = 'isyeniben@gmail.com'
MAX_AGE    = 90


def main():
    
    def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

if __name__ == "__main__":
    main()