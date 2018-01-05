from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, FreeInterval

from errors import error_str

from scripts import timeparsing as TP

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username (preferred name would be ideal: first_last)', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    course = IntegerField('Course Number (e.g. 105, 40, etc.)', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    course = IntegerField('Course Number (e.g. 105, 40, etc.)', validators=[DataRequired()])
    clear = BooleanField('Clear all free times (this cannot be undone)')
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please choose a different username.')

class DelForm(FlaskForm):
    interval_id = IntegerField("Delete Interval by id, where ([id=n]: Free from Sunday at ...)", validators=[DataRequired()])
    submit = SubmitField("Delete Interval")

class AddForm(FlaskForm):
    sd = StringField("Start day of interval: (e.g. Monday, tuesday,   fRiDaY , etc.) ", validators=[DataRequired()])
    st = StringField("Start time of interval (military time is OK): (e.g. 1:30pm, 23:00, 12:01am, etc.)", validators=[DataRequired()])
    ed = StringField("End day of interval:", validators=[DataRequired()])
    et = StringField("End time of interval:", validators=[DataRequired()])
    submit = SubmitField('Add Interval')

    def validate_sd(self, sd):
        try:
            TP.parse_day(sd.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "error(s) in day submission: "))

    def validate_ed(self, ed):
        try:
            TP.parse_day(ed.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "error(s) in day submission: "))

    # both of these functions need the two seperate trys to avoid double submission
    # this is a hacky fix and if there is a better way to do it i'd love to know
    def validate_st(self, st):
        try:
            TP.parse_hours(st.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "error(s) in time submission: "))
        try:
            TP.parse_mins(st.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "error(s) in time submission: "))

    def validate_et(self, et):
        try:
            TP.parse_hours(et.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "error(s) in time submission: "))
        try:
            TP.parse_mins(et.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "error(s) in time submission: "))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')



