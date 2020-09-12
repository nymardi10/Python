import boto3


client = boto3.client('iam')


def main():

    storeage = client.list_users()
    for user in storeage['Users']:
        username = user['UserName']
        tags = client.list_user_tags(UserName=username)
        for alltags in tags['Tags']:
            key_ids = alltags['Key']
            if key_ids:
                delete_key(username, key_ids)
                untag_user(username, key_ids)
            else:
                print('nothing')

def untag_user(uname, key_id):
    client.untag_user(
    UserName=uname,
    TagKeys=[
        key_id, 
    ]
)   

def delete_key(uname, key_ids):
    client.delete_access_key(UserName=uname, AccessKeyId=key_ids)

        

if __name__ == "__main__":
    main()