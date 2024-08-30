from flask import Flask, flash, redirect, render_template, url_for, request

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from flask_bcrypt import Bcrypt

import json
from dotenv import load_dotenv
import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content


load_dotenv(override=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisissecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

genai.configure(api_key=os.getenv("API_KEY"))

# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8000,
  "response_schema": content.Schema(
        type = content.Type.OBJECT,
        properties = {
                "tasks": content.Schema(
                        type = content.Type.ARRAY,
                        items = content.Schema(
                                type = content.Type.STRING,
                        ),
                ),
        },
  ),
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="You are writing TODO list. OUTPUT tasks to achive this goal. Tasks must not contain period at the end. The list of tasks must be in format of JSON array. The list must be without numeration. You must output only tasks or steps. If user tells somthing apart from his goals, task to complete, you must return empty answer.",
)

@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))

class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(20), nullable=False, unique=True)
        password = db.Column(db.String(80), nullable=False)
class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(100), nullable=False)
        is_complete = db.Column(db.Boolean, default=False, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)

        def __repr__(self) -> str:
                return f"Task {self.id}"
class Goal(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(75), nullable=False)

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

class GoalForm(FlaskForm):
        your_goal = StringField(validators=[InputRequired(), Length(min=1, max=100)], render_kw={'autofocus': True})
        
        submit = SubmitField("Submit")

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
        task_goals = db.session.query(Task, Goal).join(Task, Goal.id == Task.goal_id).filter(Task.user_id == current_user.id)
        goals = task_goals.group_by(Goal.name).all()
        tasks = task_goals.all() 
        print(current_user.id)

        form = GoalForm()
        if form.validate_on_submit():
                response = model.generate_content(form.your_goal.data)
                if response: 
                        new_goal = Goal(name=form.your_goal.data)
                        db.session.add(new_goal)
                        db.session.commit()
                        response_json = json.loads(response.text)
                        tasks_array = response_json["tasks"]
                        for task in tasks_array:
                                new_task = Task(content=task, is_complete=False, user_id=current_user.id, goal_id=new_goal.id)
                                db.session.add(new_task)
                        db.session.commit()
                        return redirect(url_for('index'))

        return render_template("site/index.html", form=form, goals=goals, tasks=tasks)

@app.route('/complete_task', methods=['POST', 'GET'])
@login_required
def complete_task():
        id = request.get_json()['id']
        db.session.execute(db.update(Task).where(Task.id == id).values(is_complete=~Task.is_complete))
        db.session.commit()
        return {
            'response' : '(un)checked!'
        }

@app.route('/delete', methods=['POST', 'GET'])
@login_required
def delete():
        id = request.get_json()['id']
        db.session.execute(db.delete(Task).where(Task.goal_id == id))
        db.session.execute(db.delete(Goal).where(Goal.id == id))
        db.session.commit()
        return {
            'response' : 'deleted!'
        }

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