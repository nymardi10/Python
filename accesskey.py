import datetime, boto3, csv
from collections import namedtuple
from botocore.exceptions import ClientError
from datetime import datetime, timezone

client = boto3.client('iam')
ses = boto3.client('ses')

EMAIL_FROM = 'nymardi@gmail.com'
EMAIL_TO   = 'isyeniben@gmail.com'
MAX_AGE    = 0

def main():    
    
    paginator = client.get_paginator('list_users')

    for response in paginator.paginate():

        for user in response['Users']:
            username = user['UserName']
            
            res = client.list_access_keys(UserName=username)
            #for access_key in res['AccessKeyMetadata']:
                
                #access_key_id = access_key['AccessKeyId']
            create_date = res['AccessKeyMetadata']['AccessKeyId']
            print('<----------====================---------->')
                #key_last_used(access_key_id, username)

            age = days_old(create_date)
            if age < MAX_AGE:
                continue
            else:
                access_key_count(username)
                print(username)

                   
                
def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

def key_last_used(key_id, user_name):
    key_list = client.get_access_key_last_used(AccessKeyId=key_id)
    if key_list['AccessKeyLastUsed']['ServiceName'] == 'N/A':
        client.delete_access_key(UserName=user_name,AccessKeyId=key_id)
        print(f'Deleted user {user_name} Access Key')
    else:
        new_access_key = client.create_access_key(UserName=user_name)
        print(new_access_key['AccessKey']['UserName'],
        new_access_key['AccessKey']['AccessKeyId'],
        new_access_key['AccessKey']['SecretAccessKey'])

def access_key_count(user_name):
    User = namedtuple('User', 'user arn user_creation_time password_enabled password_last_used password_last_changed password_next_rotation mfa_active access_key_1_active access_key_1_last_rotated access_key_1_last_used_date access_key_1_last_used_region access_key_1_last_used_service access_key_2_active access_key_2_last_rotated access_key_2_last_used_date access_key_2_last_used_region access_key_2_last_used_service cert_1_active cert_1_last_rotated cert_2_active cert_2_last_rotated')
    response = client.get_credential_report()
    body = response['Content'].decode('utf-8')
    lines = body.split('\n')
    users = [User(*line.split(',')) for line in lines[1:]]
    #print(users)

    for user in users:
        if (user.access_key_1_active == 'true' and user.access_key_2_active == 'false'):
            #client.create_access_key(UserName=user_name) 
            print(user.user)        
        else:
            continue


if __name__ == '__main__':
        main()