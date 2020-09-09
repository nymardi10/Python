import boto3

client = boto3.client('secretsmanager')

def main():


    create_secret()



def create_secret():
    response = client.create_secret(
    ClientRequestToken='UserName-90ab-cdef-fedc-ba987SECRET1',
    Description='UserName AWS secret created with the CLI',
    Name='UserName',
    SecretString='{"Access Key":"AKHOiho9JK00LK","Secret Key":"BnQw!XDWgaE?!@#eartg345gk4eT9XGTT29"}',
    )

    print(response)

def list_secret():
    response = client.list_secrets()
    print(response['SecretList'][0]['ARN'])


if __name__ == "__main__":
    main()