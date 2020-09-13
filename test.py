import boto3
from datetime import datetime, timezone

client = boto3.client('iam')

def main():
    check_for_deletion()
    
def check_for_deletion():
    userpaginate = client.get_paginator('list_users')
    print('Looking for inactive keys that are older then 90 days')
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
                #access_key_age = key['CreateDate']
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
                                if age >= 0:
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
        print('All Keys up to date')

def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

if __name__ == "__main__":
    main()