import sys
import boto3
import itertools
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError

client = boto3.client('iam')
secrets = boto3.client('secretsmanager')
sts = boto3.client('sts')

MAX_AGE = 90
DAYS = 90

def main():
    #check_for_old_keys()
    #check_for_tags()
    #create_new_access_keys()
    check_for_accesskeys()
    

def check_for_old_keys():    
    mysecretslist = secrets.list_secrets()    
    for user in client.list_users()['Users']:
        username = user['UserName']
        #print(username)
        counter=0
        res = client.list_access_keys(UserName = username)
        print(username)
        """
        if not res['AccessKeyMetadata']: 
         for statuses in res['AccessKeyMetadata']:
            create_date = statuses['CreateDate']
            now = datetime.now(timezone.utc)
            age = now - create_date
            counter=0
            #tags_list = client.list_user_tags(UserName= user['UserName'])
            if statuses['Status'] == "Inactive":
                print(username)
                print(statuses['AccessKeyId'],statuses['Status'])  
                client.delete_access_key(
                UserName=username,
                AccessKeyId=statuses['AccessKeyId']
                )
                
            if not res['AccessKeyMetadata']:
                print('here')
            if age.days > MAX_AGE :
                print(username)
                client.update_access_key(
                UserName=username,
                AccessKeyId=statuses['AccessKeyId'],
                Status='Inactive')
                """
                
    
def check_for_tags():

    identity = sts.get_caller_identity()
    account = identity['Account']
    header_printed = False

    count = 0
    today = datetime.now(timezone.utc)

    # Get all IAM users in this AWS account
    for user in client.list_users()['Users']:
        arn = user['Arn']
        username = user['UserName']

    # Get all access keys for this IAM user
        keys = client.list_access_keys(UserName=username)

    # Test each key's age and print those that are too old
        for key in keys['AccessKeyMetadata']:
            akid = key['AccessKeyId']
            created = key['CreateDate']
            created_delta = today - created

        # if this access key is older than DAYS
            if created + timedelta(days=DAYS) > today:
                count += 1
                response = client.get_access_key_last_used(AccessKeyId=akid)
                akid_last_used = response['AccessKeyLastUsed']

                if not header_printed:
                    header_printed = True
                    print(f'Account, Username, Access Key, Age, Last Used')

                print(f'{account}, {username}, {akid}, {created_delta.days} ', end = '')

            # Only keys that have actually been used will have last used date
                if 'LastUsedDate' in akid_last_used:
                    last_used = akid_last_used['LastUsedDate']
                    last_used_delta = today - last_used
                    print(last_used_delta.days)
                else:
                    print('none')

    sys.exit(count)

def create_new_access_keys():
    userlist=[]
    for user in client.list_users()['Users']:
        username = user['UserName']
        for akid in client.list_access_keys(UserName=username)['AccessKeyMetadata']:
            list_user=akid['UserName']
            userlist+=list_user
            count = userlist.count(list_user)
            if count == 0:
                client.create_access_key(
                UserName=username
                )  
    

def check_for_accesskeys():
    userlist=[]
    for user in client.list_users()['Users']:
        username = user['UserName']
        for akid in client.list_access_keys(UserName=username)['AccessKeyMetadata']:
            list_user=akid['UserName']
            userlist+=[list_user]
            count = userlist.count(list_user)
            now = datetime.now(timezone.utc)
            if count > 1:
                for userkeyage in userlist:
                    create_date = akid['CreateDate']
                    age = now - create_date
                    if age.days < 1:
                        client.update_access_key(
                        UserName=list_user,
                        AccessKeyId=akid['AccessKeyId'],
                        Status='Inactive')
                if akid['Status'] == 'Inactive':
                    client.delete_access_key(
                    UserName=list_user,
                    AccessKeyId=akid['AccessKeyId']
                    )
                    if count == 2:
                        print()          
                while (userlist.count(username)):
                    userlist.remove(username)
    for remove_list in userlist:
        client.create_access_key(
        UserName=remove_list
        )
                            
    print('All users are up to date with two keys')               

if __name__ == "__main__":
    main()