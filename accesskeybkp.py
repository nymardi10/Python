import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
ses = boto3.client('ses')
from botocore.exceptions import ClientError

EMAIL_FROM = 'nymardi@gmail.com'
EMAIL_TO   = 'isyeniben@gmail.com'
MAX_AGE    = 90


def main():
    
    
    paginator = client.get_paginator('list_users')

    for response in paginator.paginate():

        for user in response['Users']:
            username = user['UserName']
            res = client.list_access_keys(UserName=username)
            for access_key in res['AccessKeyMetadata']:
                    access_key_id = access_key['AccessKeyId']
                    create_date = access_key['CreateDate']
                    print(f'User:{username} {access_key_id} {create_date}')

                    age = days_old(create_date)
                    if age < MAX_AGE:
                        continue
                    print(f'Key {access_key_id} for {username} expired 'f'(age={age} days.')
                
                    #client.update_access_key(UserName=username, AccessKeyId=access_key_id, Status='Inactive')

                   # send_email_report(EMAIL_TO, username, age, access_key_id)

def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

def send_email_report(email_to, username, age, access_key_id):
        data = (f'Access Key {access_key_id} for user {username} deactivated it is  {age} days old.')

        try:
            response =ses.send_email(
             Source=EMAIL_FROM,
             Destination={
                'ToAddresses':[EMAIL_TO]
             },
             Message={
                'Subject':{
                    'Data': ('AWS IAM Access Hey Rotation - Deactivation of ' 
                             f'Access Keys: {access_key_id}')
                },
                'Body': {
                    'Text': {
                        'Data': data
                    }
                }
            })
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:" + response['MessageId'])

if __name__ == '__main__':
        main()