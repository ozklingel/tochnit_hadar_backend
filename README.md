# Prerequisites to install:

1. Python

2. postgres+psql (sql shell) -set password to postgres as "TH"!!!

# Installation:
1. Clone repo from this github

2. Create virtual environment:
	```bash
	python -m venv venv && source venv/bin/activate
	```

(Python interpreter path, for IDE debugging: `./venv/bin/python`)

3. Install required libraries:
	```bash
	pip install -r requirements.txt
	```

3. Run db_create.sql script to create db on sql shell :
	```bash
	createdb t_h
	psql -U postgres t_h -f C:/path/to/db_create.sql
	```

4. On project repo run flask:
	```bash
	flask run
	```
	(For debugging, add the `--debug` flag)
