connect:
ssh -i Downloads/"th04.pem" ec2-user@ec2-16-171-62-190.eu-north-1.compute.amazonaws.com
ssh -i Downloads/th04.pem ubuntu@ec2-13-53-126-125.eu-north-1.compute.amazonaws.com

deploy:
scp -i Downloads/th04.pem  Downloads/ezyzip.zip ubuntu@ec2-13-53-126-125.eu-north-1.compute.amazonaws.com:~
ssh -i Downloads/th04.pem ubuntu@ec2-13-53-126-125.eu-north-1.compute.amazonaws.com
tar cvf flaskapp.tar flaskapp/
rm -rf flaskapp/*
mv ezyzip.zip flaskapp/
cd flaskapp
unzip ezyzip
A

sed -i 's/postgresql:\/\/postgres:TH@localhost\/t_h/postgresql:\/\/thdb1:oenk76178@thdb1.cmveev2ncszs.eu-north-1.rds.amazonaws.com:5432\/thDB/' config.py
chmod 777 /home/ubuntu/flaskapp/data/to_csv.csv
chmod 777 /home/ubuntu/flaskapp/system_export
sudo service apache2 restart

instal server:
chmod o+x /home/username/
sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
sudo tail -f /var/log/apache2/error.log

conect db:
psql --host=thdb1.cmveev2ncszs.eu-north-1.rds.amazonaws.com --port=5432 --dbname=thDB --username=thdb1
oenk76178
\dt
redis-server
redis-cli -h 127.0.0.1 -p 6379 
FLUSHALL

INSERT INTO apprentice (apprentice_id, accompany_id, name) 
  VALUES (549247615, 549247616,  'אהוד');



front restart:
dart run build_runner watch --delete-conflicting-outputs





