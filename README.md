prerequests installed:

1.python:pip+flask+virtualenv

2.postgress (sql shell)

3.emulator (install android studio)

installation:
0.create local DB:
       on  sql shell :\n
                  CREATE DATABASE t_h;
                  \c t_h;
            	CREATE TABLE user1 (
            	id  uuid, 
            	password  char(20),
            	email char(20)
            	);
            	INSERT INTO user1 VALUES (1, 'Cheese', 'bla');
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


