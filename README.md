# prerequests installed:

1.python:pip+flask+virtualenv (be able to run hhelo world app like in  https://pythonbasics.org/flask-tutorial-hello-world/)

2.postgress (sql shell) -set password to postgress as "TH"!!!

3.emulator (install android studio)


# installation:

0.create local DB:
       on  sql shell :
       

CREATE TABLE  notifications(

id int,
apprenticeid int ,
userid int ,
event text DEFAULT '',
date DATE ,
allreadyread boolean DEFAULT False,
numOfLinesDisplay int  ,
details text DEFAULT '',
PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(userid)
      REFERENCES user1(id),
CONSTRAINT fk_2
      FOREIGN KEY(apprenticeid)
      REFERENCES apprentice(id)
	 

);

CREATE TABLE institutions(
id int,
address  text DEFAULT '',
city_id text DEFAULT '',
phone  text DEFAULT '',
contact_name text DEFAULT '',
contact_phone text DEFAULT '',
logo_path text DEFAULT '',
name char (50) DEFAULT '',
owner_id text DEFAULT '',
    PRIMARY KEY(id)

);

CREATE TABLE  clusters(

id int,
name text DEFAULT '',
    PRIMARY KEY(id)

);

 CREATE TABLE  cities(
id int,
name text DEFAULT '',
cluster_id int DEFAULT 0,
    PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(cluster_id)
      REFERENCES clusters(id)
);

CREATE TABLE user1(
id int,
role_id text DEFAULT '',
first_name text DEFAULT '',
last_name text DEFAULT '',
teudatZehut  text DEFAULT '',
email  text DEFAULT '',
birthday  date ,
eshcol  text DEFAULT '',
institution_id  int DEFAULT 0,
address  text DEFAULT '',
creationDate  date ,
photo_path  text DEFAULT '',
city_id int DEFAULT 0,
cluster_id int DEFAULT 0,
notifyStartWeek boolean DEFAULT False,
notifyMorning boolean DEFAULT True,
notifyDayBefore boolean DEFAULT False,

PRIMARY KEY(id)
,
CONSTRAINT fk_1
      FOREIGN KEY(institution_id)
      REFERENCES institutions(id),
CONSTRAINT fk_2
      FOREIGN KEY(city_id)
      REFERENCES cities(id),
CONSTRAINT fk_3
      FOREIGN KEY(cluster_id)
      REFERENCES clusters(id)

);



CREATE TABLE apprentice(
id int,
accompany_id int ,
last_name text DEFAULT '',
maritalStatus text DEFAULT '',
marriage_date date ,
teacher_grade_b_phone text DEFAULT '',
teacher_grade_b text DEFAULT '',
teacher_grade_b_email  text DEFAULT '',
teacher_grade_a_phone text DEFAULT '',
teacher_grade_a_email  text DEFAULT '',
teacher_grade_a text DEFAULT '',
highSchoolInstitution text DEFAULT '',
high_school_teacher_phone text DEFAULT '',
high_school_teacher text DEFAULT '',
high_school_name text DEFAULT '',
high_school_teacher_email text DEFAULT '',
contact1_email text DEFAULT '',
contact1_first_name text DEFAULT '',
contact1_last_name text DEFAULT '',
contact1_phone text DEFAULT '',
contact2_email text DEFAULT '',
contact2_phone text DEFAULT '',
contact2_first_name text DEFAULT '',
contact2_last_name text DEFAULT '',
contact3_phone text DEFAULT '',
contact3_first_name text DEFAULT '',
contact3_last_name text DEFAULT '',
contact3_email text DEFAULT '',
militaryCompoundId text DEFAULT '',
unit_name text DEFAULT '',
serve_type text DEFAULT '',
paying boolean DEFAULT False,
release_date date,  
recruitment_date date ,
onlineStatus int DEFAULT 0,
matsber int DEFAULT 0,
thPeriod text DEFAULT '',
password text DEFAULT '',	
phone  text DEFAULT '',
email  text DEFAULT '',
birthday  date ,
eshcol  text DEFAULT '',
institution_id  int DEFAULT 0,
address  text DEFAULT '',
creationDate  text DEFAULT '',
photo_path  text DEFAULT '',
city_id int DEFAULT 0,
cluster_id int DEFAULT 0,
army_role text DEFAULT '',
militaryPositionOld text DEFAULT ''   , 
militaryUpdatedDateTime date ,
educationalInstitution text DEFAULT '', 
educationFaculty text DEFAULT '',       
workOccupation text DEFAULT '',         
workType text DEFAULT '',               
workPlace text DEFAULT '',              
workStatus text DEFAULT '',  
militaryPositionNew text DEFAULT '',                                  
first_name text DEFAULT '',
PRIMARY KEY(id)
,
CONSTRAINT fk_1
      FOREIGN KEY(institution_id)
      REFERENCES institutions(id),
CONSTRAINT fk_2
      FOREIGN KEY(city_id)
      REFERENCES cities(id),
CONSTRAINT fk_3
      FOREIGN KEY(cluster_id)
      REFERENCES clusters(id)
);


CREATE TABLE  contact_forms(

id int,
created_by_id int  ,
created_for_id int  ,
created_at DATE ,
subject text DEFAULT '',
content text DEFAULT '',
allreadyread boolean DEFAULT False,
attachments text DEFAULT '',

PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(created_by_id)
      REFERENCES user1(id),
CONSTRAINT fk_2
      FOREIGN KEY(created_for_id)
      REFERENCES user1(id)


);
CREATE TABLE  visits(

id int,
apprentice_id int  ,
user_id int  ,
visit_in_army boolean DEFAULT False,
visit_date DATE ,
note text DEFAULT '',
title text DEFAULT '',
allreadyread boolean DEFAULT False,
PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(user_id)
      REFERENCES user1(id),
CONSTRAINT fk_2
      FOREIGN KEY(apprentice_id)
      REFERENCES apprentice(id)

);



INSERT INTO institutions (id, address, city_id, phone, contact_name, contact_phone, logo_path, name, owner_id) VALUES
 (0, 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h');
 INSERT INTO clusters (id, name) VALUES 
(0, '');
INSERT INTO cities (id, name, cluster_id) VALUES
 (0, 'aa', 0);
INSERT INTO user1 (id, role_id, first_name, last_name, teudatZehut, email, birthday, eshcol, institution_id, address, creationdate, photo_path, city_id, cluster_id, notifystartweek, notifymorning, notifydaybefore) VALUES
 (523301800, '1', 'עוז', 'קלי', '313387', 'o@x.x', '1999-09-09', '', 0, '', '1999-09-09', '', 0, 0, False,False ,False );

INSERT INTO apprentice (id, accompany_id, last_name, maritalstatus, marriage_date, teacher_grade_b_phone, teacher_grade_b, 
teacher_grade_b_email, teacher_grade_a_phone, teacher_grade_a_email, teacher_grade_a, highschoolinstitution, 
high_school_teacher_phone, high_school_teacher, high_school_name, high_school_teacher_email, contact1_email,
 contact1_first_name, contact1_last_name, contact1_phone, contact2_email, contact2_phone, contact2_first_name,
  contact2_last_name, contact3_phone, contact3_first_name, contact3_last_name, contact3_email, militarycompoundid, 
  unit_name, serve_type, paying, release_date, recruitment_date, onlinestatus, matsber, thperiod, password, phone, email,
   birthday, eshcol, institution_id, address, creationdate, photo_path, city_id, cluster_id, army_role, militarypositionold,
    militaryupdateddatetime, educationalinstitution, educationfaculty, workoccupation, worktype, workplace, workstatus,
     militarypositionnew, first_name) 
     VALUES (523301801,523301800, 'a', 'b', '1995-09-09', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'l', 'o', 'p', 'q', '', '', '',
      '', '', '', '', '', '', '', '', '',NULL , '1995-09-09', '1995-09-09', 0, 0, '', 'd', 'f', 'g', '1995-09-09', 'h', 0, 'j', 'k', 'l',
       0, 0, '0', '0', '1995-09-09', 'r', 't', 'y',
       'u', 'i', 'o', 'p', 'b');

INSERT INTO visits (id, apprentice_id, user_id, visit_in_army, visit_date, note, title, allreadyread) VALUES 
(0, 523301801, 523301800,False , '1999-09-09', 'hi', 'bi', NULL);
INSERT INTO contact_forms (id, created_by_id, created_for_id, created_at, subject, content, allreadyread) 
VALUES (0, 523301800, 523301800, '1999-09-09', 'hi', 'bi', False);





        


       
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
