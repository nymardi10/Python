import sys
import boto3
import itertools
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError

client = boto3.client('iam')
secrets = boto3.client('secretsmanager')
sts = boto3.client('sts')
ses = boto3.client('ses')

MAX_AGE = 90
DAYS = 90
EMAIL_FROM='nymardi@gmail.com'

def main():
    #check_and_list_access_keys()
    rotate_accesskeys()
    
def check_and_list_access_keys():

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
            access_key_ids = key['AccessKeyId']
            created = key['CreateDate']
            created_delta = today - created

        # if this access key is older than DAYS
            if created + timedelta(days=DAYS) > today:
                count += 1
                response = client.get_access_key_last_used(AccessKeyId=access_key_ids)
                access_key_ids_last_used = response['AccessKeyLastUsed']

                if not header_printed:
                    header_printed = True
                    print(f'Account, Username, Access Key, Age, Last Used')

                print(f'{account}, {username}, {access_key_ids}, {created_delta.days} ', end = '')

            # Only keys that have actually been used will have last used date
                if 'LastUsedDate' in access_key_ids_last_used:
                    last_used = access_key_ids_last_used['LastUsedDate']
                    last_used_delta = today - last_used
                    print(last_used_delta.days)
                else:
                    print('none')

    sys.exit(count)

def rotate_accesskeys():
    userlist=[]
    for user in client.list_users()['Users']:
        username = user['UserName']
        for access_key_ids in client.list_access_keys(UserName=username)['AccessKeyMetadata']:
            list_user=access_key_ids['UserName']
            userlist+=[list_user]
            count = userlist.count(list_user)
            now = datetime.now(timezone.utc)
            key_last_used = client.get_access_key_last_used(
            AccessKeyId=access_key_ids['AccessKeyId']
            )
            if count >= 1:
                for userkeyage in userlist:
                    create_date = access_key_ids['CreateDate']
                    age = now - create_date
                    print('exit 1')
                    if age.days < 0 and key_last_used['AccessKeyLastUsed']['ServiceName'] == 'N/A':
                        client.update_access_key(
                        UserName=list_user,
                        AccessKeyId=access_key_ids['AccessKeyId'],
                        Status='Inactive')
                        print('exit 2')
                if age.days < 3 and (access_key_ids['Status'] == 'Inactive' or key_last_used['AccessKeyLastUsed']['ServiceName'] == 'N/A'):
                        client.delete_access_key(
                        UserName=list_user,
                        AccessKeyId=access_key_ids['AccessKeyId']
                        )
                        print('exit 3')
            if count == 2:
                print('exit 4')
                #print('Deleting Inactive Access Keys')          
                while (userlist.count(username)):
                    userlist.remove(username)
    for remove_list in userlist:
        client.create_access_key(
        UserName=remove_list
        )
                            
    print('All users are up to date')       

    def send__key_email_report(email_to):
        data = (f'User {email_to} Access Key Inactivated. Please login to Secret Manager in order to retrieve new Access Key')
        response =ses.send_email(
        Source=EMAIL_FROM,
        Destination={
           'ToAddresses':[email_to]
             },
             Message={
                'Subject':{
                    'Data': ('AWS IAM Access Key Info')
                },
                'Body': {
                    'Text': {
                        'Data': data
                    }
                }
            })
        
        print("Email sent! Message ID:" + response['MessageId'])        

if __name__ == "__main__":
    main()