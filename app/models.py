from app import db, helptf
from datetime import datetime
import requests
import json

#  app.config['STEAM_API_KEY']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.BigInteger)
    created_ts = db.Column(db.DateTime, default=datetime.utcnow)
    is_mentor = db.Column(db.Boolean, default=0)
    nickname = db.Column(db.String(32))  # personaname
    avatar32 = db.Column(db.String(128))  # avatar
    avatar64 = db.Column(db.String(128))  # avatarmedium
    avatar184 = db.Column(db.String(128))  # avatarfull
    profile_url = db.Column(db.String(128))  # profileurl
    last_seen = db.Column(db.DateTime)  # lastlogoff
    steam_last_online_ts = db.Column(db.BigInteger)
    steam_account_created_date = db.Column(db.DateTime)  # timecreated
    steam_real_name = db.Column(db.String(128))  # realname
    steam_status = db.Column(db.Integer)  # personastate
    steam_last_online_calculated = db.Column(db.DateTime)
    # ############### Mentor Profile ########################## #
    world_part = db.Column(db.String(10))
    acceptable_age_13_15 = db.Column(db.Boolean)
    acceptable_age_15_18 = db.Column(db.Boolean)
    acceptable_age_18_plus = db.Column(db.Boolean)
    birth_year = db.Column(db.Integer)
    voice_chat = db.Column(db.Boolean)
    languages_speaking = db.Column(db.String(256))
    languages_typing = db.Column(db.String(256))
    scout = db.Column(db.Boolean)
    soldier = db.Column(db.Boolean)
    pyro = db.Column(db.Boolean)
    demoman = db.Column(db.Boolean)
    heavy = db.Column(db.Boolean)
    engineer = db.Column(db.Boolean)
    medic = db.Column(db.Boolean)
    sniper = db.Column(db.Boolean)
    spy = db.Column(db.Boolean)
    discord = db.Column(db.String(128))
    about_me = db.Column(db.String(4096))
    active_coach = db.Column(db.Boolean)
    approved = db.Column(db.Boolean)
    updated_datetime = db.Column(db.DateTime)

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
        if r.json()['response']['players'][0].get('lastlogoff'):
            u['steam_last_online_ts'] = r.json()['response']['players'][0]['lastlogoff']
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
            'steamid': str(self.steamid),  # 17-digits number is above
            # JavaScript's capacity for integer so steamid should be
            # converted to string
            'is_mentor': self.is_mentor,
            'nickname': self.nickname,
            'avatar32': self.avatar32,
            'avatar64': self.avatar64,
            'avatar184': self.avatar184,
            'profile_url': self.profile_url,
            'last_seen': self.last_seen,
            'steam_last_online_ts': self.steam_last_online_ts,
            'steam_account_created_date': self.steam_account_created_date,
            'steam_real_name': self.steam_real_name,
            'steam_status': self.steam_status,
            'world_part': self.world_part,
            'acceptable_age_13_15': self.acceptable_age_13_15,
            'acceptable_age_15_18': self.acceptable_age_15_18,
            'acceptable_age_18_plus': self.acceptable_age_18_plus,
            'birth_year': self.birth_year,
            'voice_chat': self.voice_chat,
            'languages_speaking': self.languages_speaking,
            'languages_typing': self.languages_typing,
            'scout': self.scout,
            'soldier': self.soldier,
            'pyro': self.pyro,
            'demoman': self.demoman,
            'heavy': self.heavy,
            'engineer': self.engineer,
            'medic': self.medic,
            'sniper': self.sniper,
            'spy': self.spy,
            'discord': self.discord,
            'about_me': self.about_me,
            'active_coach': self.active_coach,
        }

    def __repr__(self):
        return '<User %r>' % self.nickname
