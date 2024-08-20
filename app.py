from flask import Flask, flash, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisissecretkey'
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(20), nullable=False, unique=True)
        password = db.Column(db.String(80), nullable=False)
class MyTask(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(100), nullable=False)
        def __repr__(self) -> str:
                return f"Task {self.id}"

class RegistrationForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'autofocus': True})
        
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
        
        confirm_password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
        
        submit = SubmitField("Register")

        def validate_password(self, password, confirm):
                if password != confirm:
                        raise ValidationError(
                                "Passswords must be the same."
                        )


        def validate_username(self, username):
                existing_user_username = User.query.filter_by(
                        username=username.data).first()
                
                if existing_user_username:
                       raise ValidationError(
                              "That username already exists. Please choose a different one."
                       )
class LoginForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'autofocus': True})
        
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
        
        submit = SubmitField("Login")

@app.route('/')
def index():
        return render_template("site/index.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
        form = RegistrationForm()
        return render_template("auth/register.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
        form = LoginForm()
        return render_template("auth/login.html", form=form)

if __name__ == "__main__":
        with app.app_context():
                db.create_all()
        app.run(debug=True)