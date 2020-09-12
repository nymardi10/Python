import boto3
from datetime import datetime, timezone

client = boto3.client('iam')
secret = boto3.client('secretsmanager')
ses = boto3.client('ses')

EMAIL_FROM   = 'isyeniben@gmail.com'
MAX_AGE      = 0

def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
        res = client.list_access_keys(UserName=username)
        for status in res['AccessKeyMetadata']:
            access_key_id = status['AccessKeyId']
            create_date = status['CreateDate']
            age = days_old(create_date)
            if age >= MAX_AGE:
                print("Creating " + username + " key and set it to Active")
                create_tags(username, access_key_id)
                create_access_key(username)   
                send_email_report(username, username, MAX_AGE , username)

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
         
def create_access_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    create_secret(key_id, secret_key, uname) 

def create_secret(access_key, secret_key, uname):
    secret.update_secret(
    SecretId=uname,
    Description=uname,
    SecretString='{} {}'.format('AccessKey: ' + access_key,'SecretKey: ' + secret_key)
    )

def send_email_report(email_to, username, age, access_key_id):
        data = (f'New Access Key for user {username} created. To retrive the new key, please login to Secret Manager')
        response =ses.send_email(
        Source=EMAIL_FROM,
        Destination={
           'ToAddresses':[email_to]
             },
             Message={
                'Subject':{
                    'Data': ('AWS IAM Access Key Info')
                },
                'Body': {
                    'Text': {
                        'Data': data
                    }
                }
            })
        
        print("Email sent! Message ID:" + response['MessageId'])
    
if __name__ == "__main__":
    main()