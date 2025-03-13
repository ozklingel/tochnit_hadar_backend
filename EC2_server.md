# Flask backend for TH project

The backend consists of a Flask server and a PostgreSQL database.

# server creation
1. follow this video to create the nginx 
https://www.youtube.com/watch?v=ct1GbTvgVNM

use this link in order to copy past the commends 
https://github.com/yeshwanthlm/YouTube/blob/main/flask-on-aws-ec2.md

2. clone the github backend project to helloworld dir
or zip th project localy and upload the hello world dir.
you can use this link:https://www.ezyzip.com/zip-folder-online.html

3. make sure to comment the following link in /etc/nginx/sites-available/default:
try_files $uri $uri/ =404;

4. restart the services:
sudo systemctl restart helloworld
sudo systemctl restart nginx