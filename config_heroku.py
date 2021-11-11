import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    STEAM_API_KEY = os.environ.get('STEAM_API_KEY')
    OPENID_PROVIDERS = [{'name': 'Steam', 'url': 'https://steamcommunity.com/openid'}]
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_MENTORS_PER_REQUEST = 50
