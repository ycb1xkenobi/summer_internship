import os
import secrets

import posts as posts
from PIL import Image
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import form, PasswordField, StringField, BooleanField, SubmitField
from passwords import create_password
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed

app = Flask(__name__)
app.secret_key = 'ABC123'
app.config['FLASK_ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

roles = ['Студент', 'Преподаватель', 'Не зарегистрирован', 'Админ']


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')




@app.route('/')
@login_required
def index():
    return render_template("base.html")

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts, form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')


    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        password = Users.query.filter_by(password=form.password.data).first()
        if user and password:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)





@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/sss")
def sss():
    return redirect(url_for('sss'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data



        db.session.commit()
        flash('Вы обновили свой аккаунт!', 'Поздравляем')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route('/test')
@login_required
def test():
    return render_template('test.html')


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)

    return response


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class RegisterPage(BaseView):
    @expose('/')
    def any_page(self):
        return self.render('register.html')


admin = Admin(app, 'Админ панель', template_mode='bootstrap3')
admin.add_view(ModelView(Users, db.session, name='Пользователи'))
admin.add_view(RegisterPage(name='Регистрация пользователей'))

class LoginForm(FlaskForm):
    email = StringField('Электронная почта',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class UpdateAccountForm(FlaskForm):
    username = StringField('Имя и Фамилия',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Электронная почта',
                        validators=[DataRequired(), Email()])

    picture = FileField('Обновить фотографию', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Обновить')



    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')





if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)