from app import db
from datetime import datetime
import requests
import json

#  app.config['STEAM_API_KEY']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.Integer)
    created_ts = db.Column(db.DateTime, default=datetime.utcnow)
    is_coach = db.Column(db.Boolean, default=0)
    nickname = db.Column(db.String(32))  # personaname
    avatar32 = db.Column(db.String(128))  # avatar
    avatar64 = db.Column(db.String(128))  # avatarmedium
    avatar184 = db.Column(db.String(128))  # avatarfull
    profile_url = db.Column(db.String)  # profileurl
    last_seen = db.Column(db.DateTime)  # lastlogoff
    steam_account_created_date = db.Column(db.DateTime)  # timecreated
    steam_real_name = db.Column(db.String(128))  # realname

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def update_profile(self):
        if 'STEAM_API_KEY' not in app.config or \
                not app.config['STEAM_API_KEY']:
            return 'Error: steam api key is not defined'
        r = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}').format(app.config['STEAM_API_KEY'], self.steamid)
        if r.status_code != 200:
            return 'Retrieving user data has failed (' + \
                r.status_code + ')'
        self.nickname = r.json()['response']['players'][0].personaname
        self.avatar32 = r.json()['response']['players'][0].avatar
        self.avatar64 = r.json()['response']['players'][0].avatarmedium
        self.avatar184 = r.json()['response']['players'][0].avatarfull
        self.profile_url = r.json()['response']['players'][0].profileurl
        self.last_seen = r.json()['response']['players'][0].lastlogoff
        self.steam_account_created_date = r.json()['response']['players'][0].timecreated
        self.steam_real_name = r.json()['response']['players'][0].realname

    def __repr__(self):
        return '<User %r>' % self.nickname
