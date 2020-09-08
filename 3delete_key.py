import boto3


client = boto3.client('iam')


def main():

    storeage = client.list_users()
    for user in storeage['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        tags = client.list_user_tags(UserName=username)
        key_ids = tags['Tags'][0]['Key']
        for access_key in res['AccessKeyMetadata']:
            access_key_id = access_key['AccessKeyId']
            statusid = access_key['Status']
            key_list = client.get_access_key_last_used(AccessKeyId=access_key_id)
            if statusid == 'Inactive':
                
                print(username)
                print(key_ids)
                delete_access_key(UserName=username, AccessKeyId=key_ids)
                untag_user(username, access_key_id)

def untag_user(uname, key_id):
    client.untag_user(
    UserName=uname,
    TagKeys=[
        key_id, 
    ]
)   

def delete_access_key(uname, key_ids):
    client.delete_access_key(UserName=username, AccessKeyId=key_ids)

        

if __name__ == "__main__":
    main()