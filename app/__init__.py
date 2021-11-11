from flask import Flask
import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config, DevConfig


helptf = Flask(__name__)

#  dev database switch
dev_mode = False
if dev_mode:
    helptf.config.from_object(DevConfig)
else:
    helptf.config.from_object(Config)

lm = LoginManager(helptf)
lm.init_app(helptf)
oid = OpenID(helptf, os.path.join(basedir, 'tmp'))
db = SQLAlchemy(helptf)
migrate = Migrate(helptf, db)

from app import routes
