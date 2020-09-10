import boto3

client = boto3.client('iam')
secret = boto3.client('secretsmanager')
ses = boto3.client('ses')
from botocore.exceptions import ClientError

EMAIL_FROM = 'nymardi@gmail.com'
EMAIL_TO   = 'isyeniben@gmail.com'
MAX_AGE    = 90


def main():

    response = client.list_users()
    for user in response['Users']:
        username = user['UserName']
        print(username)
        create_access_key(username)   
        send_email_report(EMAIL_TO, username, MAX_AGE , username)       
         
def create_access_key(uname):
    list_users = client.create_access_key(UserName=uname)
    key_id = list_users['AccessKey']['AccessKeyId']
    secret_key = list_users['AccessKey']['SecretAccessKey']
    #print(list_users['AccessKey']['AccessKeyId'])
    #print(list_users['AccessKey']['SecretAccessKey'])
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
           'ToAddresses':[EMAIL_TO]
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