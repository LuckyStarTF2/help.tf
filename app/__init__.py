from flask import Flask
import os
import logging
from flask_login import LoginManager
from flask_openid import OpenID
from config_heroku import basedir
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config_heroku import Config


helptf = Flask(__name__)

helptf.config.from_object(Config)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
helptf.logger.addHandler(stream_handler)

lm = LoginManager(helptf)
lm.init_app(helptf)
oid = OpenID(helptf, os.path.join(basedir, 'tmp'))
db = SQLAlchemy(helptf)
migrate = Migrate(helptf, db)

from app import routes
