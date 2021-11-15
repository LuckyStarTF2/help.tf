from app import db, helptf
from datetime import datetime
import requests
import json

#  app.config['STEAM_API_KEY']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.BigInteger)
    created_ts = db.Column(db.DateTime, default=datetime.utcnow)
    is_coach = db.Column(db.Boolean, default=0)
    nickname = db.Column(db.String(32))  # personaname
    avatar32 = db.Column(db.String(128))  # avatar
    avatar64 = db.Column(db.String(128))  # avatarmedium
    avatar184 = db.Column(db.String(128))  # avatarfull
    profile_url = db.Column(db.String(128))  # profileurl
    last_seen = db.Column(db.DateTime)  # lastlogoff
    steam_account_created_date = db.Column(db.DateTime)  # timecreated
    steam_real_name = db.Column(db.String(128))  # realname
    steam_status = db.Column(db.Integer)  # personastate

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
        if 'STEAM_API_KEY' not in helptf.config or \
                not helptf.config['STEAM_API_KEY']:
            return 'Error: steam api key is not defined'
        r = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}'.\
                         format(helptf.config['STEAM_API_KEY'], self.steamid))
        if r.status_code != 200:
            return 'Retrieving user data has failed (' + \
                r.status_code + ')'
        u = {}
        if r.json()['response']['players'][0].get('personaname'):
            u['nickname'] = r.json()['response']['players'][0]['personaname']
        if r.json()['response']['players'][0].get('avatar'):
            u['avatar32'] = r.json()['response']['players'][0]['avatar']
        if r.json()['response']['players'][0].get('avatarmedium'):
            u['avatar64'] = r.json()['response']['players'][0]['avatarmedium']
        if r.json()['response']['players'][0].get('avatarfull'):
            u['avatar184'] = r.json()['response']['players'][0]['avatarfull']
        if r.json()['response']['players'][0].get('profileurl'):
            u['profile_url'] = r.json()['response']['players'][0]['profileurl']
        if r.json()['response']['players'][0].get('lastlogoff'):
            u['last_seen'] = r.json()['response']['players'][0]['lastlogoff']
        if r.json()['response']['players'][0].get('timecreated'):
            u['steam_account_created_date'] = r.json()['response']['players'][0]['timecreated']
        if r.json()['response']['players'][0].get('realname'):
            u['steam_real_name'] = r.json()['response']['players'][0]['realname']
        if r.json()['response']['players'][0].get('personastate'):
            u['steam_status'] = r.json()['response']['players'][0]['personastate']
        return u

    def serialize(self):
        return {
            # 'id': self.id,
            'steamid': self.steamid,
            # 'created_ts': self.created_ts,
            # 'is_coach': self.is_coach,
            'nickname': self.nickname,
            'avatar32': self.avatar32,
            'avatar64': self.avatar64,
            'avatar184': self.avatar184,
            'profile_url': self.profile_url,
            'last_seen': self.last_seen,
            'steam_account_created_date': self.steam_account_created_date,
            'steam_real_name': self.steam_real_name,
            'steam_status': self.steam_status,
        }

    def __repr__(self):
        return '<User %r>' % self.nickname
