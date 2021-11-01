from app import helptf, db, lm, oid
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, redirect, session, url_for, request, g, jsonify
from app.forms import LoginForm
from app.models import User
from datetime import datetime
import requests


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@helptf.before_request
def before_request():
    g.user = current_user


@oid.after_login
def after_login(resp):
    # return redirect(url_for('index'))
    # return str(resp.identity_url)
    # <- resp.identity_url это как раз-таки
    # https://steamcommunity.com/openid/id/number

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        user = User.query.filter_by(steamid=int(str(resp.identity_url).split("/")[5])).first()
        if user is None:
            # create a user
            user = User(steamid=str(resp.identity_url).split("/")[5])
            db.session.add(user)
            db.session.commit()
            print("New user signed up: " + str(resp.identity_url).split("/")[5])
            login_user(user, remember=True)
            print("User just logged in: " + str(resp.identity_url).split("/")[5])
            return redirect(url_for('index'))
        else:
            # authenticate a user
            login_user(user, remember=True)
            print("User just logged in: " + str(resp.identity_url).split("/")[5])
            return redirect(url_for('index'))


@helptf.route('/')
@helptf.route('/index')
def index():
    if g.user.is_authenticated:
        return render_template('authenticated.html')
    else:
        return render_template('notauthenticated.html')


@helptf.route('/auth', methods=['GET', 'POST'])
@oid.loginhandler
def auth():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = True
        return oid.try_login('https://steamcommunity.com/openid', ask_for=['nickname'])
    return render_template('auth.html',
                           form=form,
                           providers={'name': 'Steam', 'url': 'https://steamcommunity.com/openid'},
                           next=url_for('index'))


@helptf.route('/update_profile')
@login_required
def update_profile():
    u = current_user.update_profile()
    current_user.nickname = u['nickname']
    current_user.avatar32 = u['avatar32']
    current_user.avatar64 = u['avatar64']
    current_user.avatar184 = u['avatar184']
    current_user.profile_url = u['profile_url']
    current_user.last_seen = datetime.fromtimestamp(u['last_seen'])
    current_user.steam_account_created_date = datetime.fromtimestamp(u['steam_account_created_date'])
    current_user.steam_real_name = u['steam_real_name']
    db.session.commit()
    return redirect(url_for('index'))


@helptf.route('/update_all_profiles')
@login_required
def update_all_profiles():
    items_per_page = 2  # steam id check limit
    if current_user.steamid != 76561198126840092:  # me
        return redirect(url_for('index'))
    if 'STEAM_API_KEY' not in helptf.config or \
            not helptf.config['STEAM_API_KEY']:
        return 'Error: steam api key is not defined'
    users_list = User.query.all()
    times_to_repeat = divmod(len(users_list), items_per_page)[0]
    for i in range(times_to_repeat + 1):
        list_tmp = []
        for j in range(items_per_page):
            if j + (i*items_per_page) < len(users_list):
                list_tmp.append(users_list[j + (i*items_per_page)].steamid)
        r = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}'.format(helptf.config['STEAM_API_KEY'], ','.join(str(steamid) for steamid in list_tmp)))
        if r.status_code != 200:
            return 'Retrieving user data has failed (' + \
                r.status_code + ')'
        print(','.join(str(steamid) for steamid in list_tmp) + ": " + str(r.status_code))
        response_users = r.json()['response']['players']
        for ru in response_users:
            User.query.filter_by(steamid=ru['steamid']).\
                update({'nickname': ru['personaname'],
                        'avatar32': ru['avatar'],
                        'avatar64': ru['avatarmedium'],
                        'avatar184': ru['avatarfull'],
                        'profile_url': ru['profileurl'],
                        'last_seen': datetime.fromtimestamp(ru['lastlogoff']),
                        'steam_account_created_date': datetime.fromtimestamp(ru['timecreated']),
                        'steam_real_name': ru['realname'],
                        'steam_status': ru['personastate']})
        db.session.commit()
    return str(len(users_list)) + ' users were updated successfully with ' + \
           str(times_to_repeat + 1) + ' requests'


@helptf.route('/u/<steamid>')
@helptf.route('/id/<steamid>')
def u(steamid):
    user = User.query.filter_by(steamid=steamid).first_or_404()
    return render_template('u.html', user=user)


@helptf.route('/getallmentors')
def get_all_mentors():
    page = request.args.get('page', 1, type=int)
    mentors = User.query.filter_by(is_coach=1).order_by(User.is_coach)\
        .paginate(page, helptf.config['JSON_MENTORS_PER_REQUEST'], False)
    return jsonify(mentors=[e.serialize() for e in mentors.items])
