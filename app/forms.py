from flask_wtf import FlaskForm
from wtforms import BooleanField
# from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    # openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=True)


class CSRFForm(FlaskForm):
    remember_me = BooleanField('remember_me', default=True)
