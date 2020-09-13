import boto3
from datetime import datetime, timezone

client = boto3.client('iam')

def main():
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
                access_key_age = key['CreateDate']
                if tags['Tags']:
                    for tag in tags['Tags']:
                        if tag['Key'] == 'active_key_id':
                           active_key_value = tag['Value']
                deactivate_all = False
                for key in acc_key_to_delete['AccessKeyMetadata']:
                    if tags['Tags']:
                        for tag in tags['Tags']:
                         #print(tag)
                         if tag['Key'] == 'active_key_id':
                           active_key_value = tag['Value']
                           if key['AccessKeyId'] == active_key_value:
                            create_date = key['CreateDate']
                            age = days_old(create_date)
                            if age >=1:
                              deactivate_all = True
                              break
                if deactivate_all:  
                    for key in acc_key_to_delete['AccessKeyMetadata']:
                        if key['AccessKeyId'] != active_key_value:
                            client.update_access_key(
                            UserName=username['UserName'],
                            AccessKeyId=key['AccessKeyId'],
                            Status='Inactive')

def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days
               
if __name__ == "__main__":
    main()