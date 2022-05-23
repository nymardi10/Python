import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
secret = boto3.client('secretsmanager')
ses = boto3.client('ses')

EMAIL_FROM   = 'email@company.com'
MAX_AGE      = 90
INACTIVE_DAYS = 100
DELETE_DAYS = 110


#Create new Access Key function
def create_acc_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    create_secret(key_id, secret_key, uname) 
    return key_id

#Create new Secret Manager object with new Access Key information
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
                    if yes_or_no(f'User {user} Access Key is over 90 days old, do you want to create a new key?'):
                        print(f'Creating {user} Access Key')
                        create_tags(user, create_acc_key(user))
                        #send_new_key_email_report(username['UserName'])
        else:
            print('**')
            print('All Keys are up to date')
            print('-----------------------')

#Check to see if the keys ready to be inactivated and Tag for future
def check_for_deactivation():
    print('Looking for keys that are older then 90 days to de-activate')
    print('-----------------------------------------------------------')
    #List users 
    userpaginate = client.get_paginator('list_users')
    for user in userpaginate.paginate():
        for username in user['Users']:
            key_count = 0
            tags = client.list_user_tags(UserName = username['UserName'])
            acc_key_to_delete = client.list_access_keys(UserName = username['UserName'])
            #List user access keys
            for key in acc_key_to_delete['AccessKeyMetadata']:
                status = key['Status']
                if status == 'Active':
                    key_count += 1
                    #is there a Tag with access Key info
                    if key_count > 1 and tags['Tags']:
                        for tag in tags['Tags']:
                            if tag['Key'] == 'active_key_id':
                                active_key_value = tag['Value']
                deactivate_all = False #if nothing to do, set deactivate to false and continue
            for key in acc_key_to_delete['AccessKeyMetadata']:
                if tags['Tags']:
                    for tag in tags['Tags']: #start collecting Access Keys to delete
                        if tag['Key'] == 'active_key_id':
                           active_key_value = tag['Value']
                           #if tagged and older than INACTIVE_DAYS set keys to Inactive
                           if key['AccessKeyId'] == active_key_value:
                            create_date = key['CreateDate']
                            age = days_old(create_date)
                            if age >= INACTIVE_DAYS:
                              deactivate_all = True #Set deactivate to False and continue
                              break
                if deactivate_all:  
                    #Start the Inactive status for Access Keys
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
    #List users
    for user in userpaginate.paginate():
        for username in user['Users']:
            active_key_count = 0
            inactive_key_count = 0
            tags = client.list_user_tags(UserName = username['UserName'])
            acc_key_to_delete = client.list_access_keys(UserName = username['UserName'])
            #List user access keys
            for key in acc_key_to_delete['AccessKeyMetadata']:
                #is the key set to Active or Inactive and increment the variable
                if key['Status'] == 'Active':
                    active_key_count += 1
                else: 
                    inactive_key_count += 1
            if active_key_count >= 1 and inactive_key_count >= 1:
                #If there is a Tagged item , save it in a variable
                if tags['Tags']:
                    for tag in tags['Tags']:
                        if tag['Key'] == 'active_key_id':
                            active_key_value = tag['Value']
                delete_all = False
                #if the tagged item equals the inactive key, that key will be deleted
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
#Email functions per action, email functions can be combined into one, with set variables for notification
# Created multiple email functions for ease of readability   
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

def main():
    check_for_creation()
    check_for_deactivation()
    check_for_deletion()

if __name__ == "__main__":
    main()