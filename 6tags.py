import boto3

client=boto3.client('iam')

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']

        create_tags(username)
        print(username)
   
def create_tags(uname):
   client.tag_user(
    UserName=uname,
    Tags=[
        {
            'Key': 'inactive',
            'Value': 'TRUE'
       },
    ]
)




    


if __name__ == '__main__':
    main()
    