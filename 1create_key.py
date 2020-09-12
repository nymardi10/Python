import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
secret = boto3.client('secretsmanager')
ses = boto3.client('ses')

EMAIL_FROM   = 'isyeniben@gmail.com'
MAX_AGE      = 5

def main():

 check_for_creation()
 check_for_deactivation()
 check_for_deletion()

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

def check_for_creation():
    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        for status in res['AccessKeyMetadata']:
            access_key_id = status['AccessKeyId']
            create_date = status['CreateDate']
            age = days_old(create_date)
            if age >= MAX_AGE:
                print("Creating " + username + " key and set it to Active")
                create_tags(username, create_access_key(username)) 
                send_email_report(username, username, MAX_AGE , username)

def check_for_deletion():
    userpaginate = client.get_paginator('list_users')

    for user in userpaginate.paginate():
        for username in user['Users']:
            active_key_count = 0
            inactive_key_count = 0
            tags = client.list_user_tags(UserName = username['UserName'])
            acc_key_to_delete = client.list_access_keys(UserName = username['UserName'])
            for key in acc_key_to_delete['AccessKeyMetadata']:
                status = key['Status']
                if status == 'Active':
                    active_key_count += 1
                else: 
                    inactive_key_count += 1
            print(status)
            print(active_key_count)
            if active_key_count >= 1 and inactive_key_count >= 1:
                access_key_age = key['CreateDate']
                if tags['Tags']:
                    for tag in tags['Tags']:
                        if tag['Key'] == 'active_key_id':
                           print(tag['Value'])
                           active_key_value = tag['Value']
                delete_all = False
                for key in acc_key_to_delete['AccessKeyMetadata']:
                    if key['AccessKeyId'] == active_key_value:
                        create_date = key['CreateDate']
                        age = days_old(create_date)
                        if age >= 7:
                            delete_all = True
                            break
                if delete_all:  
                    for key in acc_key_to_delete['AccessKeyMetadata']:
                        if key['AccessKeyId'] != active_key_value and key['Status'] == 'Inactive':
                            client.delete_access_key(
                            UserName=username['UserName'],
                            AccessKeyId=key['AccessKeyId']
                            )

def check_for_deactivation():
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
            print(status)
            print(key_count)
            if key_count > 1:
                #for key in acc_key_to_delete['AccessKeyMetadata']:
                access_key_age = key['CreateDate']
                if tags['Tags']:
                    for tag in tags['Tags']:
                        if tag['Key'] == 'active_key_id':
                           print(tag['Value'])
                           active_key_value = tag['Value']
                deactivate_all = False
                for key in acc_key_to_delete['AccessKeyMetadata']:
                    if key['AccessKeyId'] == active_key_value:
                        create_date = key['CreateDate']
                        age = days_old(create_date)
                        if age >=6:
                            deactivate_all = True
                            break
                if deactivate_all:  
                    for key in acc_key_to_delete['AccessKeyMetadata']:
                        if key['AccessKeyId'] != active_key_value:
                            client.update_access_key(
                            UserName=username['UserName'],
                            AccessKeyId=key['AccessKeyId'],
                            Status='Inactive')
         
def create_access_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    create_secret(key_id, secret_key, uname) 
    return key_id

def create_secret(access_key, secret_key, uname):
    secret.update_secret(
    SecretId=uname,
    Description=uname,
    SecretString='{} {}'.format('AccessKey: ' + access_key,'SecretKey: ' + secret_key)
    )

def send_email_report(email_to, username, age, access_key_id):
        data = (f'New Access Key for user {username} created. To retrive the new key, please login to Secret Manager')
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