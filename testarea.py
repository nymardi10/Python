import boto3

client = boto3.client('iam')


for user in client.list_users()['Users']:
    username=user['UserName']
    for access_keys in client.list_access_keys(UserName=username)['AccessKeyMetadata']:
        access_key_list=access_keys['AccessKeyId']
        response = client.get_access_key_last_used(
        AccessKeyId=access_key_list
        )
        if response['AccessKeyLastUsed']['ServiceName'] == 'N/A':
            print(username)