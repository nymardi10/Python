import boto3

client = boto3.client('secretsmanager')

def main():


    create_secret()



def create_secret(access_key, secret_key, uname):
    response = client.create_secret(
    ClientRequestToken='UserName-90ab-cdef-fedc-ba987SECRET1',
    Description='UserName AWS secret created with the CLI',
    Name='UserName',
    SecretString='{"Access Key":{access_key},"Secret Key":{secret_key}}',
    )

    print(response)

def list_secret():
    response = client.list_secrets()
    print(response['SecretList'][0]['ARN'])


if __name__ == "__main__":
    main()