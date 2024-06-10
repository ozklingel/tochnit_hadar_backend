
DROP TABLE IF EXISTS institutions CASCADE ;
DROP TABLE IF EXISTS clusters CASCADE ;
DROP TABLE IF EXISTS users CASCADE ;
DROP TABLE IF EXISTS apprentices CASCADE ;
DROP TABLE IF EXISTS tasks CASCADE ;
DROP TABLE IF EXISTS messages CASCADE ;
DROP TABLE IF EXISTS reports CASCADE ;
DROP TABLE IF EXISTS regions CASCADE ;
DROP TABLE IF EXISTS task_user_made CASCADE ;
DROP TABLE IF EXISTS cities CASCADE ;
DROP TABLE IF EXISTS user_role CASCADE ;
DROP TABLE IF EXISTS role CASCADE ;
DROP TABLE IF EXISTS base CASCADE ;
DROP TABLE IF EXISTS work_status CASCADE ;
DROP TABLE IF EXISTS army_role CASCADE ;
DROP TABLE IF EXISTS spirit_status CASCADE ;
DROP TABLE IF EXISTS serve_type CASCADE ;
DROP TABLE IF EXISTS marriage_status CASCADE ;
DROP TABLE IF EXISTS madadim_setting CASCADE ;
DROP TABLE IF EXISTS message_type CASCADE ;
DROP TABLE IF EXISTS system_report CASCADE ;
DROP TABLE IF EXISTS gift CASCADE ;
DROP TABLE IF EXISTS report_type CASCADE ;
DROP TABLE IF EXISTS contacts CASCADE ;

DROP TYPE IF EXISTS message_type CASCADE ;
DROP TYPE IF EXISTS marriage_status CASCADE ;
DROP TYPE IF EXISTS serve_type CASCADE ;
DROP TYPE IF EXISTS spirit_status CASCADE ;
DROP TYPE IF EXISTS army_role CASCADE ;
DROP TYPE IF EXISTS work_status CASCADE ;
DROP TYPE IF EXISTS report_type CASCADE ;
DROP TYPE IF EXISTS relation_enum CASCADE ;


CREATE TYPE message_type AS ENUM ('un known', 'mother');
CREATE TYPE marriage_status AS ENUM ('un known', 'mother');
CREATE TYPE serve_type AS ENUM ('un known', 'mother');
CREATE TYPE spirit_status AS ENUM ('un known', 'mother');
CREATE TYPE army_role AS ENUM ('un known', 'mother');
CREATE TYPE work_status AS ENUM ('un known', 'mother');
CREATE TYPE relation_enum AS ENUM ('un known', 'mother');
CREATE TYPE report_type AS ENUM ('שיחה טלפונית', 'פגישה מקוונת', 'נסיון כושל', '5 הודעות', 'פגישה פיזית', 'מפגש קבוצתי', 'ביקור בבסיס', 'שיחת הורים',
 'ישיבת מצבר', 'הזנת מחזור', 'מפגש מחזור', 'שבת מחזור', 'עשיה לטובת בוגרים', 'כנס מלווים מקצועי חודשי', 'כנס מלווים שנתי', 'ישיבת מלוים ורכזים', 'ישיבת חודשית עם רכז', 'ישיבה מוסדית');

CREATE TABLE  clusters(

id uuid,
name text DEFAULT '',
PRIMARY KEY(id)

);

CREATE TABLE institutions(
id uuid,
cluster_id uuid,
roshYeshiva_phone text DEFAULT '',
roshYeshiva_name text DEFAULT '',
admin_phone text DEFAULT '',
admin_name text DEFAULT '',
address  text DEFAULT '',
city_id text DEFAULT '',
phone  text DEFAULT '',
contact_name text DEFAULT '',
contact_phone text DEFAULT '',
logo_path text DEFAULT '',
name text DEFAULT '',
owner_id text DEFAULT '',

PRIMARY KEY(id),
CONSTRAINT fk_1
  FOREIGN KEY(cluster_id)
  REFERENCES clusters(id)

);



CREATE TABLE  regions(

id int,
name text DEFAULT '',
PRIMARY KEY(id)

);

 CREATE TABLE  cities(
id int,
name text DEFAULT '',
region_id int ,
PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(region_id)
      REFERENCES regions(id)
);

CREATE TABLE  role(
id uuid,
name text DEFAULT '',
PRIMARY KEY(id)

);
CREATE TABLE users(
id uuid,
first_name text DEFAULT '',
phone text DEFAULT '',

last_name text DEFAULT '',
identity_id  text DEFAULT '',
email  text DEFAULT '',
birthday  date ,
institution_id  uuid ,
address  text DEFAULT '',
photo_path  text DEFAULT 'https://www.gravatar.com/avatar',
city_id int ,
cluster_id uuid ,
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

CREATE TABLE  user_role(
user_id uuid,
role_id uuid,
PRIMARY KEY(user_id,role_id),
CONSTRAINT fk_1
      FOREIGN KEY(user_id)
      REFERENCES users(id),
CONSTRAINT fk_2
      FOREIGN KEY(role_id)
      REFERENCES role(id)

);




CREATE TABLE base (
id uuid,
 name TEXT DEFAULT ''::text,
 cordinatot TEXT DEFAULT ''::text,
  PRIMARY KEY (id));

CREATE TABLE  madadim_setting(
cenes_madad_date date DEFAULT '1999-09-09',
tochnitMeet_madad_date date DEFAULT '1999-09-09',
eshcolMosadMeet_madad_date date DEFAULT '1999-09-09',
mosadYeshiva_madad_date date DEFAULT '1999-09-09',
hazana_madad_date date DEFAULT '1999-09-09',
professionalMeet_madad_date date DEFAULT '1999-09-09',
matzbarmeet_madad_date date DEFAULT '1999-09-09',
doForBogrim_madad_date date DEFAULT '1999-09-09',
basis_madad_date date DEFAULT '1999-09-09',
callHorim_madad_date date DEFAULT '1999-09-09',
groupMeet_madad_date date DEFAULT '1999-09-09',
meet_madad_date date DEFAULT '1999-09-09',
call_madad_date date DEFAULT '1999-09-09'
);


CREATE TABLE  contacts(
id uuid,
phone text DEFAULT '',
name text DEFAULT '',
email text DEFAULT '',
relation relation_enum,
PRIMARY KEY(id)

);

CREATE TABLE apprentices(
id uuid,
identity_id  text DEFAULT '',
accompany_id uuid ,
last_name text DEFAULT '',
marriage_status_id marriage_status,
marriage_date date ,
marriage_date_ivry text DEFAULT '',
military_compound_id  uuid ,
unit_name text DEFAULT '',
serve_type serve_type,
paying boolean DEFAULT False,
release_date date,
recruitment_date date ,
onlineStatus int DEFAULT 0,
matsber spirit_status,
thPeriod text DEFAULT '',
phone  text DEFAULT '',
email  text DEFAULT '',
birthday  date ,
cluster_id uuid,
institution_id  uuid ,
address  text DEFAULT '',
creationDate  text DEFAULT '',
photo_path  text DEFAULT 'https://www.gravatar.com/avatar',
city_id int ,
army_role army_role,
militaryPositionOld text DEFAULT ''   ,
militaryUpdatedDateTime date ,
highschoolinstitution text DEFAULT '',
educationalInstitution text DEFAULT '',
educationFaculty text DEFAULT '',
workOccupation text DEFAULT '',
workType text DEFAULT '',
workPlace text DEFAULT '',
work_status work_status,
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
      FOREIGN KEY(military_compound_id )
      REFERENCES Base(id),
CONSTRAINT fk_5
      FOREIGN KEY(accompany_id)
      REFERENCES users(id),
CONSTRAINT fk_3
      FOREIGN KEY(cluster_id)
      REFERENCES clusters(id)


);


CREATE TABLE  messages(
id uuid,
created_by_id uuid  ,
created_for_id uuid  ,
created_at timestamp ,
subject text DEFAULT '',
content text DEFAULT '',
allreadyread boolean DEFAULT False,
attachments text[] default '{}',
icon text DEFAULT 'empty',
description text DEFAULT '',
type message_type,
ent_group  text DEFAULT '',
PRIMARY KEY(id,created_for_id),
CONSTRAINT fk_1
      FOREIGN KEY(created_by_id)
      REFERENCES users(id),

CONSTRAINT fk_2
      FOREIGN KEY(created_for_id)
      REFERENCES users(id)


);



CREATE TABLE  reports(

id uuid,
apprentice_reported  uuid  ,
user_reported  uuid  ,
user_id uuid  ,
visit_in_army boolean DEFAULT False,
reports_date timestamp ,
note text DEFAULT '',
title report_type,
attachments text[] default '{}',
description text DEFAULT '',
allreadyread boolean DEFAULT False,
ent_group  text DEFAULT ''  ,
created_at    timestamp,
CONSTRAINT fk_1
      FOREIGN KEY(user_id)
      REFERENCES users(id),
CONSTRAINT fk_2
      FOREIGN KEY(user_reported)
      REFERENCES users(id),
CONSTRAINT fk_3
      FOREIGN KEY(apprentice_reported)
      REFERENCES apprentices(id)


);






CREATE TABLE  gift(

code text,
was_used boolean DEFAULT False,
PRIMARY KEY(code)

);

CREATE TABLE  system_report(

id uuid,
creation_date DATE DEFAULT '1999-09-09' ,
type text DEFAULT '',
related_id uuid,
value text DEFAULT '',
PRIMARY KEY(id)

);


CREATE TABLE  tasks(

id uuid,
userid uuid ,
apprentice_reported  uuid  ,
user_reported  uuid  ,
institution_reported uuid,
event text DEFAULT '',
date timestamp ,
allreadyread boolean DEFAULT False,
created_at timestamp,
Frequency_end text DEFAULT '' ,
Frequency_weekday text DEFAULT '',
Frequency_meta text DEFAULT ''  ,
details text DEFAULT '',
status text DEFAULT '',

PRIMARY KEY(id),
CONSTRAINT fk_1
      FOREIGN KEY(userid)
      REFERENCES users(id)
,
CONSTRAINT fk_2
      FOREIGN KEY(user_reported)
      REFERENCES users(id),
CONSTRAINT fk_3
      FOREIGN KEY(apprentice_reported)
      REFERENCES apprentices(id)
,CONSTRAINT fk_4
      FOREIGN KEY(institution_reported)
      REFERENCES institutions(id)

);




INSERT INTO regions (id, name) VALUES (0,'ירושלים והסביבה');;
INSERT INTO regions (id, name) VALUES (1,'יהודה ושומרון');
INSERT INTO regions (id, name) VALUES (2,'מחוז דרום');
INSERT INTO regions (id, name) VALUES (3,'מחוז צפון');
INSERT INTO regions (id, name) VALUES (4,'תל אביב והמרכז');
INSERT INTO regions (id, name) VALUES (5,'un known');

INSERT INTO clusters (id, name) VALUES ('bd65600d-8669-4903-8a14-af88203ad130', 'un known');

INSERT INTO base (id, name,cordinatot) VALUES ('bd65600d-8669-4903-8a14-af88203ad130','un known', '31.26097751244561 34.81765168465695');
INSERT INTO cities (id, name,region_id) VALUES (0,'un known', 0);
INSERT INTO institutions (id, name,cluster_id,owner_id) VALUES ('bd65600d-8669-4903-8a14-af88203ad130', 'un known','bd65600d-8669-4903-8a14-af88203ad130','bd65600d-8669-4903-8a14-af88203ad131');



INSERT INTO role (id, name) VALUES ('bd65600d-8669-4903-8a14-af88203ad130','מלווה');
INSERT INTO role (id, name) VALUES ('bd65600d-8669-4903-8a14-af88203ad131','רכז מוסד');
INSERT INTO role (id, name) VALUES ('bd65600d-8669-4903-8a14-af88203ad132','רכז אשכול');
INSERT INTO role (id, name) VALUES ('bd65600d-8669-4903-8a14-af88203ad133','אחראי תוכנית');

INSERT INTO madadim_setting (cenes_madad_date, tochnitmeet_madad_date, eshcolmosadmeet_madad_date, mosadyeshiva_madad_date, hazana_madad_date, professionalmeet_madad_date, matzbarmeet_madad_date, doforbogrim_madad_date, basis_madad_date, callhorim_madad_date, groupmeet_madad_date, meet_madad_date, call_madad_date) VALUES
 ('1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02', '1999-02-02');

INSERT INTO users (id, first_name, phone, last_name, identity_id, email, birthday, institution_id, address, photo_path, city_id, cluster_id, notifystartweek, notifymorning, notifydaybefore, notifymorning_weekly_report, notifymorning_sevev, notifydaybefore_sevev, notifystartweek_sevev, association_date) VALUES
 ('bd65600d-8669-4903-8a14-af88203ad130', 'as', '549247616', 'saasd', 'asdasd', 'zxc', '1999-03-03', 'bd65600d-8669-4903-8a14-af88203ad130', '', '', 0, 'bd65600d-8669-4903-8a14-af88203ad130',True , True, True, True, True, True, True, '1999-02-02');
INSERT INTO users (id, first_name, phone, last_name, identity_id, email, birthday, institution_id, address, photo_path, city_id, cluster_id, notifystartweek, notifymorning, notifydaybefore, notifymorning_weekly_report, notifymorning_sevev, notifydaybefore_sevev, notifystartweek_sevev, association_date) VALUES
 ('bd65600d-8669-4903-8a14-af88203ad131', 'as', 'xcasddsa', 'saasd', 'asdasd', 'zxc', '1999-03-03', 'bd65600d-8669-4903-8a14-af88203ad130', '', '', 0, 'bd65600d-8669-4903-8a14-af88203ad130',True , True, True, True, True, True, True, '1999-02-02');
INSERT INTO users (id, first_name, phone, last_name, identity_id, email, birthday, institution_id, address, photo_path, city_id, cluster_id, notifystartweek, notifymorning, notifydaybefore, notifymorning_weekly_report, notifymorning_sevev, notifydaybefore_sevev, notifystartweek_sevev, association_date) VALUES
 ('bd65600d-8669-4903-8a14-af88203ad132', 'as', 'xcasddsa', 'saasd', 'asdasd', 'zxc', '1999-03-03', 'bd65600d-8669-4903-8a14-af88203ad130', '', '', 0, 'bd65600d-8669-4903-8a14-af88203ad130',True , True, True, True, True, True, True, '1999-02-02');

INSERT INTO user_role (user_id, role_id) VALUES ('bd65600d-8669-4903-8a14-af88203ad130', 'bd65600d-8669-4903-8a14-af88203ad130');
INSERT INTO user_role (user_id, role_id) VALUES ('bd65600d-8669-4903-8a14-af88203ad131', 'bd65600d-8669-4903-8a14-af88203ad131');

INSERT INTO apprentices (id, identity_id,work_status,city_id,army_role,institution_id,cluster_id,matsber,serve_type,military_compound_id, accompany_id,  marriage_status_id,last_name, marriage_date, marriage_date_ivry, unit_name,  paying, release_date, recruitment_date, onlinestatus,  thperiod, phone, email, birthday,  address, creationdate, photo_path,   militarypositionold, militaryupdateddatetime, highschoolinstitution, educationalinstitution, educationfaculty, workoccupation, worktype, workplace,  militarypositionnew, first_name, institution_mahzor, association_date, birthday_ivry) VALUES
('bd65600d-8669-4903-8a14-af88203ad130', 'bd65600d-8669-4903-8a14-af88203ad130', 'un known', 0, 'un known', 'bd65600d-8669-4903-8a14-af88203ad130', 'bd65600d-8669-4903-8a14-af88203ad130', 'un known', 'un known', 'bd65600d-8669-4903-8a14-af88203ad130', 'bd65600d-8669-4903-8a14-af88203ad130', 'un known', '', '1999-09-09', '', '', True, '1999-09-09', '1999-09-09', 0, '', '', '', '1999-09-09', 0, '', '', '', '1999-09-09', '', '', '', '', '', '', '', '', '', '1999-09-09', '');

