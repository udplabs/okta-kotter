from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(4, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class ProfileForm(FlaskForm):
    display_name = StringField('Display name', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField()
