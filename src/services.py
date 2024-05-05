import redis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

red = redis.StrictRedis(host='localhost', port=6379, db=0)
