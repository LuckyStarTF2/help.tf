from flask import Flask
import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

helptf = Flask(__name__)
helptf.config.from_object('config')
db = SQLAlchemy(helptf)
lm = LoginManager(helptf)
lm.init_app(helptf)
oid = OpenID(helptf, os.path.join(basedir, 'tmp'))
migrate =Migrate(helptf, db)

from app import routes
