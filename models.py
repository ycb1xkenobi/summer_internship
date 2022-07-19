
from __init__ import db
from flask_login import UserMixin



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    group = db.Column(db.String(100), nullable=False)
    yearadmission = db.Column(db.String(100), nullable=False)


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String)
    data = db.Column(db.Text)
    mark = db.Column(db.String(2), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(30))
    text = db.Column(db.Text(2000), nullable=False)
    answer = db.Column(db.Text(1000), nullable=False)
    fromuser = db.Column(db.String(100), nullable=False)
    fromuserid = db.Column(db.String(100), nullable=False)
    touser = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(100), nullable=False)

    # status 0 - выполненые 1 - бессрочные 2 - срочные 3 - закрепленные 4 - просмотрено(оценено)
