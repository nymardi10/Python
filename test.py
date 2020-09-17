import boto3
import itertools
from datetime import datetime, timezone

client = boto3.client('iam')
secrets = boto3.client('secretsmanager')
MAX_AGE = 90
def main():
    check_for_users()

def check_for_users():    
    userlist = client.list_users()
    mysecretslist = secrets.list_secrets()    
    for user in userlist['Users']:
        username = user['UserName']
        counter=0
        tags_list = client.list_user_tags(UserName= user['UserName'])
        res = client.list_access_keys(UserName = user['UserName'])
        for statuses in res['AccessKeyMetadata']:
            create_date = statuses['CreateDate']
            now = datetime.now(timezone.utc)
            age = now - create_date
            if statuses['Status'] == "Inactive":
                print(username)
                print(statuses['AccessKeyId'],statuses['Status'])  
                client.delete_access_key(
                UserName=username,
                AccessKeyId=statuses['AccessKeyId']
                )
            elif age.days > MAX_AGE:
                print(username)
                client.update_access_key(
                UserName=username,
                AccessKeyId=statuses['AccessKeyId'],
                Status='Inactive')

if __name__ == "__main__":
    main()