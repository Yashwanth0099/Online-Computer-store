from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.validators import ValidationError


class AuthForm(FlaskForm):
    fname = StringField("First Name")
    lname = StringField("Last Name")
    email = EmailField("email", validators=[DataRequired(), Email()])
    address = StringField("address")
    phone = StringField("Phone")
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('confirm', message='Passwords must match'), Length(8)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(),  EqualTo('password', message='Passwords must match'),Length(8)])

class RegisterForm(AuthForm):
    submit = SubmitField("Register")

class LoginForm(AuthForm):
    email = StringField("Email", validators=[DataRequired()]) 
    submit = SubmitField("Login")
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__( *args, **kwargs)
        if len(self.password.validators) >= 2:
            self.password.validators.pop(1)
        del self.confirm
        #del self.username     
    # https://wtforms.readthedocs.io/en/stable/validators/#custom-validators
    def validate_email(form, field):
        email = field.data
        from email_validator import validate_email
        if "@" in email:
            try:
                validate_email(email)
            except:
                raise ValidationError("Invalid email address")
        return True

class ProfileForm(AuthForm):
    current_password = PasswordField("current password", validators=[Optional()])
    # https://wtforms.readthedocs.io/en/3.0.x/forms/#form-inheritance
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__( *args, **kwargs)
        # replace required validator with optional
        self.password.validators[0]=Optional()
        self.confirm.validators[0]=Optional()
    submit = SubmitField("Update")