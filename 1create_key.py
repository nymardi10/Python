import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
secret = boto3.client('secretsmanager')
ses = boto3.client('ses')

EMAIL_FROM   = 'nymardi@gmail.com'
MAX_AGE      = 10
INACTIVE_DAYS = 11
DELETE_DAYS = 12


def main():

 check_for_creation()
 check_for_deactivation()
 check_for_deletion()

def create_acc_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    create_secret(key_id, secret_key, uname) 
    return key_id

def create_secret(access_key, secret_key, uname):
    userlist = uname
    mysecretslist = secret.list_secrets()
    secretlist = []
    for secretslists in mysecretslist['SecretList']:
        secretlist += [secretslists['Name']]
    if uname not in secretlist:
        print(uname)
        secret.create_secret(Name=uname)
    else:
        secret.update_secret(
        SecretId=uname,
        Description=uname,
        SecretString='{} {}'.format('AccessKey: ' + access_key,'SecretKey: ' + secret_key)
        )

def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days    

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

def check_for_creation():
    userpaginate = client.get_paginator('list_users')
    print('Checking for old keys')
    print('*')
    for users in userpaginate.paginate():
        for username in users['Users']:
            user = username['UserName']
            res = client.list_access_keys(UserName = user)
            for status in res['AccessKeyMetadata']:
                access_key_id = status['AccessKeyId']
                create_date = status['CreateDate']
                age = days_old(create_date)
                if age >= MAX_AGE:
                    if yes_or_no(f'User {user} Access Key is over 90 days old, do you want to create a new key?'):
                        print(f'Creating {user} Access Key')
                        create_tags(user, create_acc_key(user))
                        #send_new_key_email_report(username['UserName'])
        else:
            print('**')
            print('All Keys are up to date')
            print('-----------------------')

def check_for_deactivation():
    print('Looking for keys that are older then 90 days to de-activate')
    print('-----------------------------------------------------------')
    userpaginate = client.get_paginator('list_users')
    for user in userpaginate.paginate():
        for username in user['Users']:
            key_count = 0
            tags = client.list_user_tags(UserName = username['UserName'])
            acc_key_to_delete = client.list_access_keys(UserName = username['UserName'])
            for key in acc_key_to_delete['AccessKeyMetadata']:
                status = key['Status']
                if status == 'Active':
                    key_count += 1
                    if key_count > 1:
                        if tags['Tags']:
                            for tag in tags['Tags']:
                                if tag['Key'] == 'active_key_id':
                                    active_key_value = tag['Value']
                deactivate_all = False
                for key in acc_key_to_delete['AccessKeyMetadata']:
                    if tags['Tags']:
                        for tag in tags['Tags']:
                         if tag['Key'] == 'active_key_id':
                           active_key_value = tag['Value']
                           if key['AccessKeyId'] == active_key_value:
                            create_date = key['CreateDate']
                            age = days_old(create_date)
                            if age >= INACTIVE_DAYS:
                              deactivate_all = True
                              break
                if deactivate_all:  
                    for key in acc_key_to_delete['AccessKeyMetadata']:
                        if key['AccessKeyId'] != active_key_value:
                            client.update_access_key(
                            UserName=username['UserName'],
                            AccessKeyId=key['AccessKeyId'],
                            Status='Inactive')
                            send_inactive_key_email_report(username['UserName'])

def check_for_deletion():
    userpaginate = client.get_paginator('list_users')
    print('Looking for inactive keys to delete')
    print('-----------------------------------')
    for user in userpaginate.paginate():
        for username in user['Users']:
            active_key_count = 0
            inactive_key_count = 0
            tags = client.list_user_tags(UserName = username['UserName'])
            acc_key_to_delete = client.list_access_keys(UserName = username['UserName'])
            for key in acc_key_to_delete['AccessKeyMetadata']:
                if key['Status'] == 'Active':
                    active_key_count += 1
                else: 
                    inactive_key_count += 1
            if active_key_count >= 1 and inactive_key_count >= 1:
                if tags['Tags']:
                    for tag in tags['Tags']:
                        if tag['Key'] == 'active_key_id':
                            active_key_value = tag['Value']
                delete_all = False
                for key in acc_key_to_delete['AccessKeyMetadata']:
                  if tags['Tags']:
                    for tag in tags['Tags']:
                        if tag['Key'] == 'active_key_id':
                            active_key_value = tag['Value']
                            if key['AccessKeyId'] == active_key_value:
                                create_date = key['CreateDate']
                                age = days_old(create_date)
                                if age >= DELETE_DAYS:
                                    delete_all = True
                                    break
                if delete_all:  
                    for key in acc_key_to_delete['AccessKeyMetadata']:
                        if key['AccessKeyId'] != active_key_value and key['Status'] == 'Inactive':
                            print(f'Deleting access key for user account: ' + username['UserName'])
                            client.delete_access_key(
                            UserName=username['UserName'],
                            AccessKeyId=key['AccessKeyId']
                            )
                            send_delete_key_email_report(username['UserName'])
        print('Check Complete')
        print('--------------')
       
def send_new_key_email_report(email_to):
        data = (f'New Access Key for user {email_to} created. Please login to Secret Manager in order to retrieve your new Access Key')
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

def send_inactive_key_email_report(email_to):
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

def send_delete_key_email_report(email_to):
        data = (f'User {email_to} Access Key DELETED. Please login to Secret Manager in order to retrieve and replace Access Key')
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