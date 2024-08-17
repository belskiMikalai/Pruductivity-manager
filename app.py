from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class MyTask(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(100), nullable=False)
        def __repr__(self) -> str:
                return f"Task {self.id}"

@app.route('/')
def index():
        return render_template("index.html")

if __name__ == "__main__":
        with app.app_context():
                db.create_all()
        app.run(debug=True)