# prerequests installed:

1.python:pip+flask+virtualenv (be able to run hhelo world app like in  https://pythonbasics.org/flask-tutorial-hello-world/)

2.postgress (sql shell) -set password to postgress as "TH"!!!

3.emulator (install android studio)


# installation:

0.create local DB:
       on  sql shell :
       
        CREATE DATABASE t_h;
        \c t_h;
	CREATE TABLE user1(
	ID int,
	Role char(20),	
	PrivateName char(20),
	familyName char(20),
	image char(20),
	phone  char(20),
	email  char(20),
	birthday  char(20),
	eshcol  char(20),
	apprentice  char(20),
	Mosad  char(20),
	address  char(20),
	creationDate  char(20),
	password char(20)
	);

	
	CREATE TABLE Apprentice(
	ID int, 
	PrivateName char(20),
	familyName char(20),
	image char(20),
	phone  char(20),
	email  char(20),
	eshcol  char(20),
	HighschoolName  char(20),
	YeshivaName  char(20),
	HomeAddress  char(20),
	BasisAddress  char(20),
	ArmyUnit  char(20),
	FamilyStatus  char(20),
	fatherName  char(20),
	fatherphone  char(20),
	fatherMail  char(20),
	motherName  char(20),
	motherPhone  char(20),
	mothermail  char(20),
	YeshivaMahzore  char(20),
	RamName  char(20),
	RamPhone  char(20),
	MelaveName  char(20),
	creationDate  DATE,
	weddingDate  DATE,
	birthday  DATE,
	startArmyDate  DATE,
	LastVisitDate  DATE,
	LastConatctDate  DATE


	);
                  


       
1.download from CMD:
      git clone <this repo url>
     
      
2. Run below command inside project directory to setup environment
      ```console
      python -m venv venv
      ```

3. Activate enviroment with below command (for Windows):
      ```console
      venv\Scripts\activate
      ```

4. Run below command next to install required modules plus dependencies defined in `requirements.txt`
      ```console
      pip install -r requirements.txt
      ```

5. Run below command to start the app:
     flask run
      ```

6. All Done!! [Click Here](http://localhost:5000/) to interact with your app:u will get all user1 table content


#post installation 
for developing ,keep an eye to follow the correct architecture like in https://realpython.com/flask-blueprint/
