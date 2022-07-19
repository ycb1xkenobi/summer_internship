from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'ABC123'
app.config['FLASK_ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ROLES'] = ['Студент', 'Преподаватель', 'Админ']
app.config['ALLOWED_EXTENSIONS'] = ['zip', 'rar', 'jpg', 'jpeg' 'png', 'txt']
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1МБ

db = SQLAlchemy(app)
manager = LoginManager(app)