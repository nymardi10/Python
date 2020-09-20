Python code to inactivate AWS Access Keys older then 90 days

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