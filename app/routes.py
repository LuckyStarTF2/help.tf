from app import helptf, db, lm, oid
import os
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, redirect, session, url_for, request, g, jsonify
from app.forms import LoginForm, CSRFForm
from app.models import User
from datetime import datetime
from html import escape
import requests, time


@helptf.cli.command("update-all-profiles")
def update_all_profiles():
    items_per_page = 100  # steam id check limit
    # if current_user.steamid != 76561198126840092:  # me
    #     return redirect(url_for('index'))
    if 'STEAM_API_KEY' not in helptf.config or \
            not helptf.config['STEAM_API_KEY']:
        return 'Error: steam api key is not defined'
    users_list = User.query.all()
    helptf.logger.info('bulk profile update: {} profiles'.format(len(users_list)))
    times_to_repeat = divmod(len(users_list), items_per_page)[0]
    for i in range(times_to_repeat + 1):
        list_tmp = []
        for j in range(items_per_page):
            if j + (i*items_per_page) < len(users_list):
                list_tmp.append(users_list[j + (i*items_per_page)].steamid)
        r = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}'.format(helptf.config['STEAM_API_KEY'], ','.join(str(steamid) for steamid in list_tmp)))
        if r.status_code != 200:
            helptf.logger.error('bulk profile update has failed, code {}, error: {}'.format(str(r.status_code), r.text))
            return 'Retrieving user data has failed (' + \
                str(r.status_code) + ')'
        # print(','.join(str(steamid) for steamid in list_tmp) + ": " + str(r.status_code))
        response_users = r.json()['response']['players']
        for ru in response_users:
            User.query.filter_by(steamid=ru['steamid']).\
                update({'nickname': ru['personaname'],
                        'avatar32': ru['avatar'],
                        'avatar64': ru['avatarmedium'],
                        'avatar184': ru['avatarfull'],
                        'profile_url': ru['profileurl'],
                        'last_seen': datetime.fromtimestamp(ru['lastlogoff']),
                        'steam_last_online_ts': ru['lastlogoff'],
                        'steam_account_created_date': datetime.fromtimestamp(ru['timecreated']),
                        'steam_last_online_calculated': datetime.now() if \
                            ru['personastate'] == 1 else \
                            datetime.fromtimestamp(ru['lastlogoff']),
                        'steam_real_name': ru['realname'],
                        'steam_status': ru['personastate'],
                        'updated_datetime': datetime.now()})
        db.session.commit()
        helptf.logger.info('bulk profile update successful')
    return str(len(users_list)) + ' users were updated successfully with ' + \
           str(times_to_repeat + 1) + ' requests'


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@lm.unauthorized_handler
def unauthorized_callback():
    return redirect('/auth?next=' + request.path)


@helptf.before_request
def before_request():
    if os.environ.get('HEROKU') and not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    g.user = current_user


@oid.after_login
def after_login(resp):
    if current_user.is_authenticated:
        if request.args.get('next') \
                and request.args.get("openid_complete") == "yes":
            return redirect(request.args.get('next'))
        else:
            return redirect(url_for('index'))
    else:
        user = User.query.filter_by(steamid=int(str(resp.identity_url).split("/")[5])).first()
        if user is None:
            # create a user
            user = User(steamid=str(resp.identity_url).split("/")[5])
            db.session.add(user)
            db.session.commit()
            # print("New user signed up: " + str(resp.identity_url).split("/")[5])
            helptf.logger.info('New user {} signed up from ip {}'.format(str(resp.identity_url).split("/")[5], request.remote_addr))
            login_user(user, remember=True)
            # print("User just logged in: " + str(resp.identity_url).split("/")[5])
            update_profile()
            if request.args.get('next') \
                    and request.args.get("openid_complete") == "yes":
                return redirect(request.args.get('next'))
            else:
                return redirect(url_for('index'))
        else:
            # authenticate a user
            login_user(user, remember=True)
            helptf.logger.info('User {} ({}) logged in from ip {}'.format(str(resp.identity_url).split("/")[5], current_user.nickname, request.remote_addr))
            # print("User just logged in: " + str(resp.identity_url).split("/")[5])
            if request.args.get('next') \
                    and request.args.get("openid_complete") == "yes":
                return redirect(request.args.get('next'))
            else:
                return redirect(url_for('index'))


@helptf.route('/')
def index():
    # if g.user.is_authenticated:
    #     return render_template('authenticated.html')
    # else:
    #     return render_template('notauthenticated.html')
    # return render_template('main_page.html', user=g.user)
    return render_template('main_page.html')


@helptf.route('/auth', methods=['GET', 'POST'])
@oid.loginhandler
def auth():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = True
        return oid.try_login('https://steamcommunity.com/openid', ask_for=['nickname'])
    if request.args.get('next'):
        next = request.args.get('next')
    else:
        next = url_for('index')
    return render_template('auth.html',
                           form=form,
                           providers={'name': 'Steam', 'url': 'https://steamcommunity.com/openid'},
                           next=next)


@helptf.route('/logout')
def logout():
    helptf.logger.info('Logout user {} ({})'.format(current_user.steamid, current_user.nickname))
    logout_user()
    return redirect(url_for('index'))


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
    helptf.logger.info('Updated user info {} ({})'.format(current_user.steamid, current_user.nickname))
    return redirect(url_for('index'))


@helptf.route('/u/<steamid>')
@helptf.route('/id/<steamid>')
def u(steamid):
    user = User.query.filter_by(steamid=steamid).first_or_404()
    world_part_full = {
        'EU': 'Europe',
        'SA': 'South America',
        'NA': 'North America',
        'ASIA': 'Asia'
    }.get(user.world_part, user.world_part)
    # if user.is_mentor == 1:
    #     return render_template('u-mentor.html', user=user)
    # else:
    return render_template('u.html', user=user, world_part_full=world_part_full, title="help.tf | " + user.nickname, currentYear = datetime.now().year, str=str)


@helptf.route('/getallmentors')
def get_all_mentors():
    page = request.args.get('page', 1, type=int)
    mentors = User.query.filter_by(is_mentor=1).order_by(User.steam_last_online_calculated.desc(), User.created_ts.desc())\
       .paginate(1, 100, False)
    return jsonify(mentors=[e.serialize() for e in mentors.items])
#     mentors = User.query.filter_by(is_mentor=1).order_by(User.is_mentor)\
#     .paginate(page, helptf.config['JSON_MENTORS_PER_REQUEST'], False)
#     print(type(mentors))
#     return jsonify(mentors=mentors.all())


@helptf.route('/mentors')
def mentors():
    return render_template('mentors.html')


@helptf.route('/become-a-mentor')
def become_a_mentor():
    return render_template('mentor-short-guide.html', title="help.tf - Start")


@helptf.route('/mentor-short-guide')
def mentor_short_guide():
    return render_template('mentor-short-guide.html', title="help.tf - Start")


# @helptf.route('/you-are-awesome')
# # show this page if a mentor tries to become a mentor while being a mentor
# def you_are_awesome():
#     return render_template('mentor-short-guide.html', title="help.tf - Start")


@helptf.route('/fill-profile', methods=['GET', 'POST'])
@login_required
def fill_the_profile():
    # if current_user.is_mentor:
    #     return redirect(url_for('you_are_awesome'))
    # else:
    form = CSRFForm()
    values = {}
    errors = []
    if request.form and form.validate_on_submit():
        print(str(request.form))
        if "world-part" in request.form and request.form['world-part'] in \
                ('NA', 'EU', 'ASIA', 'SA'):
            values['world_part'] = request.form['world-part']
        else:
            errors.append("Something is wrong with world part.")
        if "13-15" in request.form:
            values['acceptable_age_13_15'] = True
        else:
            values['acceptable_age_13_15'] = False
        if "15-18" in request.form:
            values['acceptable_age_15_18'] = True
        else:
            values['acceptable_age_15_18'] = False
        if "18+" in request.form:
            values['acceptable_age_18_plus'] = True
        else:
            values['acceptable_age_18_plus'] = False
        if "birth-year" in request.form \
                and request.form['birth-year'].isnumeric():
            values['birth_year'] = request.form['birth-year']
        else:
            errors.append("Please enter a valid birth year or '0'.")
        if "voiceChatAvailable" in request.form:
            values['voice_chat'] = True
        else:
            values['voice_chat'] = False
        if "languages-speaking" in request.form \
                and request.form['languages-speaking'] != '':
            values['languages_speaking'] = request.form['languages-speaking']
        elif "voiceChatAvailable" not in request.form:
            values['languages_speaking'] = None
        else:
            errors.append("You didn't specify languages you speak.")
        if "languages-typing" in request.form \
                and request.form['languages-typing'] != '':
            values['languages_typing'] = request.form['languages-typing']
        else:
            errors.append("You didn't specify languages you can write.")
        if "scout" in request.form:
            values['scout'] = True
        else:
            values['scout'] = False
        if "soldier" in request.form:
            values['soldier'] = True
        else:
            values['soldier'] = False
        if "pyro" in request.form:
            values['pyro'] = True
        else:
            values['pyro'] = False
        if "demoman" in request.form:
            values['demoman'] = True
        else:
            values['demoman'] = False
        if "heavy" in request.form:
            values['heavy'] = True
        else:
            values['heavy'] = False
        if "engineer" in request.form:
            values['engineer'] = True
        else:
            values['engineer'] = False
        if "medic" in request.form:
            values['medic'] = True
        else:
            values['medic'] = False
        if "sniper" in request.form:
            values['sniper'] = True
        else:
            values['sniper'] = False
        if "spy" in request.form:
            values['spy'] = True
        else:
            values['spy'] = False
        if "discord" in request.form and request.form['discord'] != '':
            values['discord'] = request.form['discord']
        else:
            errors.append("Your discord username is important, please enter it.")
        if "about-me" in request.form and request.form['about-me'] != '':
            values['about_me'] = request.form['about-me']
        else:
            values['about_me'] = ''
            # ########
        if len(errors) > 0:
            # print(errors)
            helptf.logger.info('User {} ({}) didn\'t fill all the fields in becoming a mentor form'.format(current_user.steamid, current_user.nickname))
            return render_template('fill-the-profile.html', form=form,
                                   errors=errors, values=values)
        else:
            current_user.world_part = escape(values['world_part'])
            current_user.acceptable_age_13_15 = values['acceptable_age_13_15']
            current_user.acceptable_age_15_18 = values['acceptable_age_15_18']
            current_user.acceptable_age_18_plus = values[
                'acceptable_age_18_plus']
            current_user.birth_year = escape(values['birth_year'])
            current_user.voice_chat = values['voice_chat']
            current_user.languages_speaking = escape(values['languages_speaking'])
            current_user.languages_typing = escape(values['languages_typing'])
            current_user.scout = values['scout']
            current_user.soldier = values['soldier']
            current_user.pyro = values['pyro']
            current_user.demoman = values['demoman']
            current_user.heavy = values['heavy']
            current_user.engineer = values['engineer']
            current_user.medic = values['medic']
            current_user.sniper = values['sniper']
            current_user.spy = values['spy']
            current_user.discord = escape(values['discord'])
            current_user.about_me = escape(values['about_me'])
            current_user.is_mentor = True
            db.session.commit()
            helptf.logger.info('User {} ({}) just filled their profile to become a mentor'.format(current_user.steamid, escape(current_user.nickname)))
            return redirect(url_for('thanks_for_applying'))
    elif request.form:
        helptf.logger.error('CSRF error while filling mentor\'s profile for user {} ({})'.format(current_user.steamid, escape(current_user.nickname)))
    return render_template('fill-the-profile.html', form=form, values=values,
                           title="help.tf - Your Profile")

    # current_user.last_seen = datetime.fromtimestamp(u['last_seen'])
    # current_user.steam_account_created_date = datetime.fromtimestamp(u['steam_account_created_date'])
    # current_user.steam_real_name = u['steam_real_name']
    # db.session.commit()


@helptf.route('/thanks-for-applying')
def thanks_for_applying():
    return render_template('thanks-for-applying.html',
                           title="help.tf - You are now a mentor!")


@helptf.route('/debug')
def debug():
    return ''


@helptf.route('/join-the-team')
def contact():
    return render_template('contact.html', title="help.tf - Join the Team")


@helptf.route('/logger-test')
def logger_test():
    helptf.logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAA DEBUG LOGGER ENTRY')
    return 'ok'
