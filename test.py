import boto3
from datetime import datetime, timezone

client = boto3.client('iam')

def main():
    check_for_creation()
    
def check_for_creation():
    userpaginate = client.get_paginator('list_users')
    print('Checking for old keys')
    for users in userpaginate.paginate():
        for username in users['Users']:
            user = username['UserName']
            res = client.list_access_keys(UserName = user)
            print('*')
            for status in res['AccessKeyMetadata']:
                access_key_id = status['AccessKeyId']
                create_date = status['CreateDate']
                age = days_old(create_date)
                print('**')
                if age >= 0:
                    if yes_or_no(f'User {user} Access Key is over 90 days old, do you want to create a new key?'):
                        print("Creating " + username + " Access Key")
                        create_tags(username, create_acc_key(username))
        else:
            print('***')
            print('All keys are up to date')

def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

def create_acc_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    return key_id

def create_tags(uname, key_id):
    client.untag_user(
    UserName=uname,
    TagKeys=[
        "active_key_id",
    ]
)
    client.tag_user(
    UserName=uname,
    Tags=[
        {
            'Key': "active_key_id",
            'Value': key_id
       },
    ]
)

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

if __name__ == "__main__":
    main()