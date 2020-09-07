import boto3

client = boto3.client('iam')

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']

        create_access_key(username)
   
def create_access_key(uname):
    client.create_access_key(UserName=uname)
    print(uname)

    
if __name__ == "__main__":
    main()