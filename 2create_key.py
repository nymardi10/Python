import boto3

client = boto3.client('iam')

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
       
        create_access_key(username)        
        print(username)

  
def create_access_key(uname):
    list_users = client.create_access_key(UserName=uname)
    print(list_users['AccessKey']['AccessKeyId'])
    print(list_users['AccessKey']['SecretAccessKey'])

    
if __name__ == "__main__":
    main()