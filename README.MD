Inactivate AWS Access Keys that are older then 90 days.
Updates needed: If a user has more than one key, default rule is, each IAM account is allowd to have up to two keys at any given time
Decide on which to delete with following, and assign a new key
	1) Check to see if the keys are ever used
	2) or, both or only one of them are used
	3) or, which is older than 90
Important NOTE: Make sure you understand what the code does and how it will affect your environment. 
		Make sure you undestand and update the variables MAX_AGE and DAYS
		This code will delete all inactive keys without any notification...
		This code is for testing purposes only!

Algorithm is to look for keys that are inactive or never used or older than specified date
Logic is as follows
are there two keys or one for a given user?
if two keys
	is the key inactive?
	check the age and delete the key that is inactive 
		  and 
	inactivate keys	older than 90 days and notify users with appropriate email or txt
	
if one key
	Tag the current Access Key and
	create a new one, notify user that they should be 		replacing their current one.
		after 10 days, notify user and inactivate 		the tagged Access Key
	on the 11th day, notify user and delete key
