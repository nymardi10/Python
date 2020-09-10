import boto3

client = boto3.client('iam')
secret = boto3.client('secretsmanager')

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
        print(username)
        create_access_key(username)             
       

  
def create_access_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    print(list_users['AccessKey']['AccessKeyId'])
    print(list_users['AccessKey']['SecretAccessKey'])
    create_secret(key_id, secret_key, uname) 



def create_secret(access_key, secret_key, uname):
    secret.update_secret(
    SecretId=uname,
    Description=uname,
    SecretString='{} {}'.format('AccessKey: ' + access_key,'SecretKey: ' + secret_key)
    )


    
if __name__ == "__main__":
    main()