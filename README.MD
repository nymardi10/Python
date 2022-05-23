## INSTALLATION
python 3.8

### Configuration
```
vim ~/.aws/credentials
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET

vim ~/.aws/config
[default]
region=us-east-1
```

are there two keys or one?
if two keys
	check the age and delete the key that is inactive 
		  and 
	inactivate keys	older than 90 days
	
if one key
	Tag the current Access Key and
	create a new one
	after 90 days, inactivate the tagged Access Key