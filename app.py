from flask import Flask, flash, redirect, render_template, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisissecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))

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
        
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20), EqualTo('confirm_password', 'Passwords must match')])
        
        confirm_password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
        
        submit = SubmitField("Register")

        def validate_username(self, username):
                existing_user_username = User.query.filter_by(
                        username=username.data).first()
                
                if existing_user_username:
                       raise ValidationError("That username already exists. Please choose a different one.")
class LoginForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'autofocus': True})
        
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
        
        submit = SubmitField("Login")

@app.route('/')
@login_required
def index():
        return render_template("site/index.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
        form = RegistrationForm()

        if form.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(form.password.data)
                new_user = User(username=form.username.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user, remember=True)
                return redirect(url_for('index'))
        
        return render_template("auth/register.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
        form = LoginForm()
        if form.validate_on_submit():
                user = User.query.filter_by(username=form.username.data).first()
                if user:
                        if bcrypt.check_password_hash(user.password, form.password.data):
                                login_user(user, remember=True)
                                return redirect(url_for('index'))
        
        return render_template("auth/login.html", form=form)

@app.route('/logout')
@login_required
def logout():
        logout_user()
        return redirect(url_for('login'))
if __name__ == "__main__":
        with app.app_context():
                db.create_all()
        app.run(debug=True)