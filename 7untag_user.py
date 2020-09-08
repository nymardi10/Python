import boto3

client = boto3.client('iam')

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']

        untag_user(username)

def untag_user(uname):
    client.untag_user(
    UserName=uname,
    TagKeys=[
        'inactive', 
    ]
)


if __name__ == "__main__":
    main()