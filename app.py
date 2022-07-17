from flask import Flask, render_template, url_for, request, redirect, flash
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, StringField, BooleanField, SubmitField, form
from wtforms.validators import ValidationError
from werkzeug.exceptions import RequestEntityTooLarge

from passwords import create_password
from save_picture import save_picture

app = Flask(__name__)
app.secret_key = 'ABC123'
app.config['FLASK_ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ROLES'] = ['Студент', 'Преподаватель', 'Админ']
app.config['ALLOWED_EXTENSIONS'] = ['zip', 'rar', 'jpg', 'jpeg' 'png', 'txt']
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB

db = SQLAlchemy(app)
manager = LoginManager(app)


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
    touser = db.Column(db.String(100), nullable=False)


# status 0 - выполненые 1 - бессрочные 2 - срочные 3 - закрепленные
class LoginForm(FlaskForm):
    email = StringField('Электронная почта')
    password = PasswordField('Пароль')
    remember = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class UpdateAccountForm(FlaskForm):
    name = StringField('Имя')
    surname = StringField('Фамилия')
    email = StringField('Электронная почта')
    picture = FileField('Обновить фотографию')
    group = StringField('Группа')
    yearadmission = StringField('Год поступления')
    submit = SubmitField('Обновить')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Эта почта занята, выберите другую')


class RegisterPage(BaseView):
    @expose('/')
    def any_page(self):
        return render_template('register.html')


class LoginForm(FlaskForm):
    email = StringField('Электронная почта')
    password = PasswordField('Пароль')
    remember = BooleanField('Запомнить')
    submit = SubmitField('Войти')


@app.route('/')
@login_required
def index():
    return render_template("index.html")


@app.route('/admin/registerpage/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        id = db.session.query(Users).count() + 1
        password = create_password()
        userinfo = Users(id=id, email=email, password=password, role=role, name='-', surname='-', yearadmission='-', group = '-')
        try:
            if role in app.config['ROLES']:
                if '@' in email:
                    db.session.add(userinfo)
                    db.session.commit()
                    return redirect('/admin/users')
                else:
                    return ('Проверьте правильность написания почты')
            else:
                return ('Проверьте правильность написания роли')
        except:
            return ('Произошла ошибка при добавлении пользователя')
    else:
        return render_template("register.html")


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, app)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        current_user.group = form.group.data
        current_user.yearadmission = form.yearadmission.data
        db.session.commit()
        flash('Вы обновили свой аккаунт!', 'Поздравляем')
        return redirect('/account')
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.group.data = current_user.group
        form.yearadmission.data = current_user.yearadmission

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/account/<id>", methods=['GET', 'POST'])
@login_required
def watch_profiles(id):
    user = Users.query.filter_by(id=id).first()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('profile.html', user=user, image_file=image_file)


@app.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    return render_template("student.html")


@app.route('/student/upload', methods=['GET', 'POST'])
@login_required
def uploadtask():
    if request.method == 'POST':
        try:
            file = request.files['file']

            filetype = file.filename.split('.')
            filetype = filetype[1]
            if filetype in app.config['ALLOWED_EXTENSIONS']:
                if current_user.name == '-' or current_user.surname == '-' or current_user.group == '-' or current_user.yearadmission == '-':
                    return 'Измените профиль, добавьте информацию о себе'
                else:
                    upload = Tasks(filename=file.filename, data=file.read(), mark='-', status='1', date='-', text='-',
                                   answer='-', fromuser=current_user.name + ' ' + current_user.surname, touser='-',
                                   header='-')
                    db.session.add(upload)
                    db.session.commit()
                return f'Добавлено: {file.filename}'
            else:
                return 'Неверный формат файла'
        except RequestEntityTooLarge:
            return ('Файл слишком большой')

    return render_template('uploadtask.html')


@app.route('/teacher/<id>', methods=['GET', 'POST'])
@login_required
def teacher_check_task(id):
    user = Users.query.filter_by(id=id).first()
    task_all = Tasks.query.filter_by(touser=user.email)
    return render_template('teacher_check_task.html', tasks=task_all, user=user)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


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
            return redirect(next_page) if next_page else redirect('/')
        else:
            flash('Неудачный вход', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)

    return response


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


admin = Admin(app, 'Админ панель', template_mode='bootstrap3')
admin.add_view(ModelView(Users, db.session, name='Пользователи'))
admin.add_view(ModelView(Tasks, db.session, name='Задания'))
admin.add_view(RegisterPage(name='Регистрация пользователей'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
