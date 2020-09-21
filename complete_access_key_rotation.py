import sys
import boto3
import itertools
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError

client = boto3.client('iam')
secrets = boto3.client('secretsmanager')
sts = boto3.client('sts')
ses = boto3.client('ses')

MAX_AGE = 100
DAYS = 90
EMAIL_FROM='email@company.com'

def main():
    rotate_accesskeys()
 
#inactivate keys older then DAYS function
def update_keys(uname,accesskeyid):
    client.update_access_key(
    UserName=uname,
    AccessKeyId=accesskeyid,
    Status='Inactive')
#delete keys older then MAX_DAYS function
def delete_keys(uname,accesskeyid):
    client.delete_access_key(
    UserName=uname,
    AccessKeyId=accesskeyid
    )
#create new key function
def create_keys(uname):
        client.create_access_key(
        UserName=uname
        )

def rotate_accesskeys():
#Create array for user list that has two access keys
    userlist=[]
# Get all IAM users in this AWS account
    for user in client.list_users()['Users']:
        username = user['UserName']
# Get all access keys and when last used for this IAM user
        for access_key_ids in client.list_access_keys(UserName=username)['AccessKeyMetadata']:
            list_user=access_key_ids['UserName']
            userlist+=[list_user]
            count = userlist.count(list_user)
            now = datetime.now(timezone.utc)
            key_last_used = client.get_access_key_last_used(
            AccessKeyId=access_key_ids['AccessKeyId']
            )
# Test each key's age and identify those that are too old
            if count >= 1:
                for userkeyage in userlist:
                    create_date = access_key_ids['CreateDate']
                    age = now - create_date
                    print('exit 1')
# Inactivate key state if this older than DAYS
                    if age.days > DAYS:
                        update_keys(list_user,access_key_ids['AccessKeyId'])
                        print('exit 2')
# Inactivate key state if it has never been used
                    if key_last_used['AccessKeyLastUsed']['ServiceName'] == 'N/A':
                        update_keys(list_user,access_key_ids['AccessKeyId'])
# Delete keys if this access key is older than MAX_DAYS, or inactive or never used
                if age.days < MAX_AGE and (access_key_ids['Status'] == 'Inactive' or key_last_used['AccessKeyLastUsed']['ServiceName'] == 'N/A'):
                        delete_keys(list_user,access_key_ids['AccessKeyId'])
                        print('exit 3')
            if count == 2:
#if the key count for the user is 2, store the username in array   
# and
#leave only the user accounts with one key in order too create second key     
                while (userlist.count(username)):
                    userlist.remove(username)
                    print('exit 4')  
#Create new keys for user for future use                
    for remove_list in userlist:
        create_keys(remove_list)
                            
    print('All users are up to date')       


if __name__ == "__main__":
    main()