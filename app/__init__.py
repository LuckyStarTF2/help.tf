from flask import Flask
import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


helptf = Flask(__name__)
helptf.config.from_object(Config)
lm = LoginManager(helptf)
lm.init_app(helptf)
oid = OpenID(helptf, os.path.join(basedir, 'tmp'))
db = SQLAlchemy(helptf)
migrate = Migrate(helptf, db)

from app import routes
