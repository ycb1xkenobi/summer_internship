from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from passwords import create_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50), primary_key = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)
    role = db.Column(db.String(20), nullable = False)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        temp=db.get('email') #Тут
        return temp
     
    else: 
        return render_template("login.html")

@app.route('/registerusers', methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']

        password = create_password()
        id = db.session.query(Users).count() + 1

        userinfo = Users(id=id, email=email, password=password, role=role,)
        try:
            db.session.add(userinfo)
            db.session.commit()
            return redirect('/')
        except:
            return('Произошла ошибка при добавлении пользователя')
    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.run(debug = True)