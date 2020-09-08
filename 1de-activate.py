import boto3


client = boto3.client('iam')


def main():

    storeage = client.list_users()
    for user in storeage['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        for status in res['AccessKeyMetadata']:
            access_key_id = status['AccessKeyId']
            key_list = client.get_access_key_last_used(AccessKeyId=access_key_id)
            
            if key_list['AccessKeyLastUsed']['ServiceName'] == 'N/A':
                create_tags(username, access_key_id)
                print("Tagging " + username + " with old key")
                client.update_access_key(
                UserName=username,
                AccessKeyId=status['AccessKeyId'],
                Status='Inactive')
                print(username)


def create_tags(uname, key_id):
       client.tag_user(
    UserName=uname,
    Tags=[
        {
            'Key': key_id,
            'Value': key_id
       },
    ]
)

if __name__ == "__main__":
    main()