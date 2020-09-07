import boto3

client = boto3.client('iam')

def main():

    response = client.list_users()
    #for user in response():

    for user in response['Users']:
        username = user['UserName']
        #users = user['Users']
        client.create_access_key(UserName=username)
        print(username)
    
if __name__ == "__main__":
    main()