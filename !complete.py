import boto3

client = boto3.client('iam')

def main():
    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        for status in res['AccessKeyMetadata']:
            access_key_id = status['AccessKeyId']
            key_list = client.get_access_key_last_used(AccessKeyId=access_key_id)
        

            de_activate (username, access_key_id)
        create_access_key(username)
        print(username)

def de_activate (uname, key_id):
    client.update_access_key(
                UserName=uname,
                AccessKeyId=key_id,
                Status='Inactive')
   
def create_access_key(uname):
    user_access_key = client.create_access_key(UserName=uname)
    print(user_access_key['AccessKey']['AccessKeyId'])
    print(user_access_key['AccessKey']['SecretAccessKey'])

    

    
if __name__ == "__main__":
    main()