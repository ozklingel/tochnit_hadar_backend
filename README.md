# prerequests installed:

1.python

2.postgress+psql (sql shell) -set password to postgress as "TH"!!!


# installation:
1.clone repo from this github

2.install requied libs:
	pip install -r requirements.txt

3.run db_create.sql script to create db  on  sql shell :
		psql -U postgres postgres -f C:/path/to/db_create.sql
 4. on project repo run :
 	flask run 
