import boto3


client = boto3.client('iam')


def main():

    storeage = client.list_users()
    for user in storeage['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        for access_key in res['AccessKeyMetadata']:
            access_key_id = access_key['AccessKeyId']
            statusid = access_key['Status']
            key_list = client.get_access_key_last_used(AccessKeyId=access_key_id)
            if key_list['AccessKeyLastUsed']['ServiceName'] == 'N/A' and statusid == 'Inactive':
                print(username)
                client.delete_access_key(UserName=username, AccessKeyId=access_key_id)
        

if __name__ == "__main__":
    main()