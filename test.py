import boto3


client = boto3.client('iam')


def main():

    client.create_user(
    UserName='anothernewguy'
    )

    client.attach_user_policy(
    UserName = 'anothernewguy',
    PolicyArn = 'arn:aws:iam::aws:policy/AdministratorAccess'
    )


if __name__ == "__main__":
    main()