
DROP TABLE IF EXISTS institutions CASCADE ;
DROP TABLE IF EXISTS clusters CASCADE ;
DROP TABLE IF EXISTS user1 CASCADE ;
DROP TABLE IF EXISTS apprentice CASCADE ;
DROP TABLE IF EXISTS contact_forms CASCADE ;
DROP TABLE IF EXISTS visits CASCADE ;
DROP TABLE IF EXISTS ent_group CASCADE ;
DROP TABLE IF EXISTS task_user_made CASCADE ;
DROP TABLE IF EXISTS regions CASCADE ;
DROP TABLE IF EXISTS cities CASCADE ;
DROP TABLE IF EXISTS task_user_made CASCADE ;
DROP TABLE IF EXISTS system_report CASCADE ;
DROP TABLE IF EXISTS base CASCADE ;
DROP TABLE IF EXISTS gift CASCADE ;


CREATE TABLE institutions(
eshcol_id text DEFAULT '',
roshYeshiva_phone text DEFAULT '',
roshYeshiva_name text DEFAULT '',
admin_phone text DEFAULT '',
admin_name text DEFAULT '',
id int,
address  text DEFAULT '',
city_id text DEFAULT '',
phone  text DEFAULT '',
contact_name text DEFAULT '',
contact_phone text DEFAULT '',
logo_path text DEFAULT '',
name text DEFAULT '',
owner_id text DEFAULT '',

    PRIMARY KEY(id)

);

CREATE TABLE  clusters(

id int,
name text DEFAULT '',
    PRIMARY KEY(id)

);

CREATE TABLE  regions(

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
      REFERENCES regions(id)
);
CREATE TABLE base (
id INTEGER NOT NULL,
 name TEXT DEFAULT ''::text,
 cordinatot TEXT DEFAULT ''::text,
  PRIMARY KEY (id));

CREATE TABLE user1(
id int,
role_ids text DEFAULT '',
first_name text DEFAULT '',
last_name text DEFAULT '',
teudatZehut  text DEFAULT '',
email  text DEFAULT '',
birthday  date ,
eshcol  text DEFAULT '',
institution_id  int DEFAULT 0,
address  text DEFAULT '',
creationDate  date ,
photo_path  text DEFAULT 'https://www.gravatar.com/avatar',
city_id int DEFAULT 0,
cluster_id int DEFAULT 0,
notifyStartWeek boolean DEFAULT False,
notifyMorning boolean DEFAULT True,
notifyDayBefore boolean DEFAULT False,

notifyMorning_weekly_report boolean DEFAULT False,
notifyMorning_sevev boolean DEFAULT False,
notifyDayBefore_sevev boolean DEFAULT False,
notifyStartWeek_sevev boolean DEFAULT False,

association_date  date ,
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
teudatZehut  text DEFAULT '',
accompany_id int ,
last_name text DEFAULT '',
maritalStatus text DEFAULT '',
marriage_date date ,
marriage_date_ivry text ,
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
contact1_relation text DEFAULT '',
contact2_email text DEFAULT '',
contact2_phone text DEFAULT '',
contact2_first_name text DEFAULT '',
contact2_last_name text DEFAULT '',
contact2_relation text DEFAULT '',
contact3_phone text DEFAULT '',
contact3_first_name text DEFAULT '',
contact3_last_name text DEFAULT '',
contact3_email text DEFAULT '',
contact3_relation text DEFAULT '',
militaryCompoundId  int DEFAULT 14509,
unit_name text DEFAULT '',
serve_type text DEFAULT '',
paying boolean DEFAULT False,
release_date date,
recruitment_date date ,
onlineStatus int DEFAULT 0,
matsber text DEFAULT '',
thPeriod text DEFAULT '',
password text DEFAULT '',
phone  text DEFAULT '',
email  text DEFAULT '',
birthday  date ,
eshcol  text DEFAULT '',
institution_id  int DEFAULT 0,
address  text DEFAULT '',
creationDate  text DEFAULT '',
photo_path  text DEFAULT 'https://www.gravatar.com/avatar',
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
institution_mahzor text DEFAULT '',
association_date date ,
birthday_ivry text DEFAULT '',

PRIMARY KEY(id)
,
CONSTRAINT fk_1
      FOREIGN KEY(institution_id)
      REFERENCES institutions(id),
CONSTRAINT fk_2
      FOREIGN KEY(city_id)
      REFERENCES cities(id),
CONSTRAINT fk_4
      FOREIGN KEY(militarycompoundid )
      REFERENCES Base(id),
CONSTRAINT fk_3
      FOREIGN KEY(cluster_id)
      REFERENCES clusters(id)

);

CREATE TABLE  contact_forms(
id int,
created_by_id int  ,
created_for_id int  ,
created_at timestamp ,
subject text DEFAULT '',
content text DEFAULT '',
allreadyread boolean DEFAULT False,
attachments text[] default '{}',
icon text DEFAULT 'empty',
description text DEFAULT '',
type text DEFAULT 'draft',
ent_group  text DEFAULT '',
PRIMARY KEY(id,created_for_id),
CONSTRAINT fk_1
      FOREIGN KEY(created_by_id)
      REFERENCES user1(id),
CONSTRAINT fk_2
      FOREIGN KEY(created_for_id)
      REFERENCES user1(id)


);

CREATE TABLE  visits(

id int,
ent_reported int  ,
user_id int  ,
visit_in_army boolean DEFAULT False,
visit_date DATE ,
note text DEFAULT '',
title text DEFAULT '',
attachments text[] default '{}',
description text DEFAULT '',
allreadyread boolean DEFAULT False,
ent_group  text DEFAULT ''  ,
created_at    timestamp,
CONSTRAINT fk_1
      FOREIGN KEY(user_id)
      REFERENCES user1(id)


);



CREATE TABLE  ent_group(

id int,
user_id int,
group_name text DEFAULT '',
PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(user_id)
      REFERENCES user1(id)

);

CREATE TABLE  gift(

code text,
was_used boolean DEFAULT False,
PRIMARY KEY(code)

);

CREATE TABLE  system_report(

id int,
creation_date DATE DEFAULT '1999-09-09' ,
type text DEFAULT '',
related_id int,
value int,
PRIMARY KEY(id)

);



CREATE TABLE  task_user_made(

id int,
userid int ,
event text DEFAULT '',
date timestamp ,
created_at timestamp,
Frequency_end text DEFAULT '' ,
Frequency_weekday text DEFAULT '',
Frequency_meta text DEFAULT ''  ,
details text DEFAULT '',
status text DEFAULT '',
subject text DEFAULT '' ,
already_read boolean DEFAULT False,

institution_id boolean DEFAULT False,
PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(userid)
      REFERENCES user1(id)



);
INSERT INTO regions (id, name) VALUES (0,'ירושלים והסביבה');;
INSERT INTO regions (id, name) VALUES (1,'יהודה ושומרון');
INSERT INTO regions (id, name) VALUES (2,'אזור דרום');
INSERT INTO regions (id, name) VALUES (3,'אזור צפון');
INSERT INTO regions (id, name) VALUES (4,'אזור המרכז');
INSERT INTO regions (id, name) VALUES (5,'un known');
INSERT INTO clusters (id, name) VALUES (0,'מרכז');
INSERT INTO clusters (id, name) VALUES (1,'דרום');
INSERT INTO clusters (id, name) VALUES (2,'צפון');