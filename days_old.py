import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
ses = boto3.client('ses')
from botocore.exceptions import ClientError

EMAIL_FROM = 'nymardi@gmail.com'
EMAIL_TO   = 'isyeniben@gmail.com'
MAX_AGE    = 0


def main():
    
    
    paginator = client.get_paginator('list_users')

    for response in paginator.paginate():

        for user in response['Users']:
            username = user['UserName']
            res = client.list_access_keys(UserName=username)
            for access_key in res['AccessKeyMetadata']:
                    access_key_id = access_key['AccessKeyId']
                    create_date = access_key['CreateDate']
                    print(access_key_id)

                    age = days_old(create_date)
                    if age < MAX_AGE:
                        continue
                    create_access_key(username)
                    print(f'Key {access_key_id} for {username} expired 'f'(age={age} days.')
                
def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

def create_access_key(uname):
    client.create_access_key(UserName=uname)
    print(uname)

if __name__ == '__main__':
        main() 