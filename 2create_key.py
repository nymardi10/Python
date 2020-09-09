import boto3

client = boto3.client('iam')
secret = boto3.client('secretsmanager')

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
        #for keys in username['AccessKeyMetadata']:
       
        create_access_key(username)   
           
        print(user)

  
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
    SecretString='{} {}'.format('Access Key: '+ access_key, 'Secret Key: '+secret_key)

    #access_key,secret_key
       
    #SecretId=uname,
    #Description=uname,
    #Name=uname,
    #SecretString= '{"Access Key":{access_key},"Secret Key":{secret_key}}'
    )


    
if __name__ == "__main__":
    main()