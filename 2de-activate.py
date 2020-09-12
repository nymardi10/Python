import boto3

client = boto3.client('iam')

def main():
    userpaginate = client.get_paginator('list_users')

    for user in userpaginate.paginate():
        for username in user['Users']:
            tags = client.list_user_tags(UserName = username['UserName'])
            acc_key_to_delete = client.list_access_keys(UserName = username['UserName'])
            if tags['Tags']:
                client.update_access_key(
                UserName=username['UserName'],
                AccessKeyId=tags['Tags'][0]['Key'],
                Status='Inactive')
               
if __name__ == "__main__":
    main()