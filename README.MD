<<<<<<< HEAD
Inactivate AWS Access Keys that are older then 90 days. Updates needed: If a user has more than one key, default rule is, each IAM account is allowd to have up to two keys at any given time Decide on which to delete with following, and assign a new key 1) Check to see if the keys are ever used 2) or, both or only one of them are used 3) or, which is older than 90 Important NOTE: Make sure you understand what the code does and how it will affect your environment. Make sure you undestand and update the DAYS variables This code will delete all inactive keys without any notification... This code is for testing purposes only!

Logic is to look for keys that are inactive or never used or older than specified date Notify user of the changes for them to update their keys with the new one Store the new key in AWS Secrets Manager, Tag the active key for future updates.
=======
Inactivate AWS Access Keys that are older then 90 days.
Updates needed: If a user has more than one key, default rule is, each IAM account is allowd to have up to two keys at any given time
Decide on which to delete with following, and assign a new key
	1) Check to see if the keys are ever used
	2) or, both or only one of them are used
	3) or, which is older than 90
Important NOTE: Make sure you understand what the code does and how it will affect your environment. 
		Make sure you undestand and update the DAYS variables 
		This code will delete all inactive keys without any notification...
		This code is for testing purposes only!

Logic  is to look for keys that are inactive or never used or older than specified date
Notify user of the changes for them to update their keys with the new one
Store the new key in AWS Secrets Manager, 
Tag the active key for future updates.
>>>>>>> 7e9df3210d0f511c407574191a66da1aeaa771d2
