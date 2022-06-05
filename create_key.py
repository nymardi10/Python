import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
secret = boto3.client('secretsmanager')
ses = boto3.client('ses')

EMAIL_FROM   = 'email@company.com'
MAX_AGE      = 90
INACTIVE_DAYS = 100
DELETE_DAYS = 110


#Calculate the age of current Access Keys function
def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days    

#Creta Tag with current Access Key information
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

#This portion is for testing before putting it in production, 
#It will confirm to validate you want to create a new Access Key
#This function will fail if used with Lambda
#If you use this with CloudWatch and Lambda, take off line 92
def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

#Search for keys that are older then MAX_AGE and do something
def check_for_creation():
    #List all users
    userpaginate = client.get_paginator('list_users')
    print('Checking for old keys')
    print('*')
    key_count=0
    for users in userpaginate.paginate():
        for username in users['Users']:
            user = username['UserName']
            res = client.list_access_keys(UserName = user)
            #list access key for user
            for status in res['AccessKeyMetadata']:
                access_key_id = status['AccessKeyId']
                create_date = status['CreateDate']
                age = days_old(create_date)
                if age >= MAX_AGE:
                    print(username['UserName'], username['CreateDate'])
        else:
            print('**')
            print('All Keys are up to date')
            print('-----------------------')

def main():
    check_for_creation()

if __name__ == "__main__":
    main()