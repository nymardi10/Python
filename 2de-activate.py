import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
MAX_AGE = 0

def main():

    storeage = client.list_users()
    for user in storeage['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        for status in res['AccessKeyMetadata']:
            access_key_id = status['AccessKeyId']
            key_list = client.get_access_key_last_used(AccessKeyId=access_key_id)
            create_date = status['CreateDate']
            age = days_old(create_date)
           
            if age > MAX_AGE or key_list['AccessKeyLastUsed']['ServiceName'] == 'N/A':
                print("Tagging " + username + " old key and set it to Inactive")
                client.update_access_key(
                UserName=username,
                AccessKeyId=status['AccessKeyId'],
                Status='Inactive')
                create_tags(username, access_key_id)
            else:
                print(username + 'Untagged')

def days_old(create_date):
        now = datetime.now(timezone.utc)
        age = now - create_date
        return age.days

def create_tags(uname, key_id):
       client.tag_user(
    UserName=uname,
    Tags=[
        {
            'Key': key_id,
            'Value': key_id
       },
    ]
)

if __name__ == "__main__":
    main()