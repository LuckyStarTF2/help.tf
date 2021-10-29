from app import helptf, db, lm, oid
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, redirect, session, url_for, request, g
from app.forms import LoginForm
from app.models import User
from datetime import datetime


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

