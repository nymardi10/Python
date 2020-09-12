import datetime, boto3, csv
from collections import namedtuple

client = boto3.client('iam')

def main():

    User = namedtuple('User', 'user arn user_creation_time password_enabled password_last_used password_last_changed password_next_rotation mfa_active access_key_1_active access_key_1_last_rotated access_key_1_last_used_date access_key_1_last_used_region access_key_1_last_used_service access_key_2_active access_key_2_last_rotated access_key_2_last_used_date access_key_2_last_used_region access_key_2_last_used_service cert_1_active cert_1_last_rotated cert_2_active cert_2_last_rotated')
    response = client.get_credential_report()
    body = response['Content'].decode('utf-8')
    lines = body.split('\n')
    users = [User(*line.split(',')) for line in lines[1:]]

    for user in users:
        if (user.access_key_1_active == 'true' and user.access_key_2_active == 'true'):
            #client.create_access_key(UserName=user)
            print(user.user)
            print("\r")


if __name__ == "__main__":
    main()