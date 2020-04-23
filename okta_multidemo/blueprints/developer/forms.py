from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Optional


class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 100)])
    grant_type = SelectField(choices=[('client_credentials', 'Client Credentials'), ('authorization_code', 'Authorization Code (PKCE)')])
    redirect_uri = StringField('Redirect URI')
