import boto3
import itertools
from datetime import datetime, timezone

client = boto3.client('iam')
secrets = boto3.client('secretsmanager')

def main():
    check_for_users()

def check_for_users():
    userlist = client.list_users()
    mysecretslist = secrets.list_secrets()
    secretlist = []
    for secretslists in mysecretslist['SecretList']:
        secretlist += [secretslists['Name']]
    for user in userlist['Users']:
        if user['UserName'] not in secretlist:
                check_for_secret(user['UserName'])
         
def check_for_secret(uname):
    print(uname)
    secrets.create_secret(Name = uname)
           

if __name__ == "__main__":
    main()