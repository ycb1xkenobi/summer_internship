from flask import Flask, render_template, url_for, request, redirect, flash
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, StringField, BooleanField, SubmitField
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
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1МБ

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
    fromuserid = db.Column(db.String(100), nullable=False)
    touser = db.Column(db.String(100), nullable=False)


# status 0 - выполненые 1 - бессрочные 2 - срочные 3 - закрепленные


class LoginForm(FlaskForm):
    email = StringField('Электронная почта')
    password = PasswordField('Пароль')
    remember = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class AddTask(FlaskForm):
    touser_field = StringField('Почта преподавателя')
    date_field = StringField('Дата конца срока (Если задание со сроком)')
    header_field = StringField('Заголовок')
    submit = SubmitField('Отправить')


class ChangePassword(FlaskForm):
    password1 = PasswordField('Введите новый пароль')
    password2 = PasswordField('Повторите новый пароль')
    submit = SubmitField('Сохранить')


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
        userinfo = Users(id=id, email=email, password=password, role=role, name='-', surname='-', yearadmission='-',
                         group='-')
        if role in app.config['ROLES']:
            user = Users.query.filter_by(email=email).first()
            if user:
                flash('Такой пользователь зарегистрирован', 'danger')
            else:
                if '@' in email:
                    db.session.add(userinfo)
                    db.session.commit()
                    flash(f'Пароль {password} для пользователя {email}')
                else:
                    flash('Это не почта!', 'danger')
        else:
            flash('Такой роли не существует', 'danger')
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


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePassword()
    if form.validate_on_submit():
        if form.password1.data == form.password2.data:
            current_user.password = form.password1.data
            db.session.commit()
            flash('Пароль обновлен')
        else:
            flash('Пароли не совпадают', 'danger')
    return render_template('changepassword.html', form=form)


@app.route("/account/<id>", methods=['GET', 'POST'])
@login_required
def watch_profiles(id_profile):
    user = Users.query.filter_by(id=id_profile).first()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('profile.html', user=user, image_file=image_file)


@app.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    return render_template("student.html")


@app.route('/student/upload', methods=['GET', 'POST'])
@login_required
def upload_task():
    form = AddTask()
    if form.validate_on_submit():
        file = request.files['file']
        if file:
            filetype = file.filename.split('.')
            filetype = filetype[1]
        else:
            filetype = 'txt'
        text = request.form.get('text_field')
        header = form.header_field.data
        date = form.date_field.data
        touser = form.touser_field.data
        status = request.form.get('select')
        check = 0
        if date and status == '2':
            check = 1
        if status == '1':
            check = 1
        try:
            user = Users.query.filter_by(email=touser).first()
            if user:
                if user.role == 'Преподаватель':
                    if text and header and touser:
                        if check == 1:
                            if filetype in app.config['ALLOWED_EXTENSIONS']:
                                if current_user.name == '-' or current_user.surname == '-' or current_user.group == '-' or current_user.yearadmission == '-':
                                    flash('Измените профиль, добавьте информацию о себе', 'danger')
                                else:
                                    upload = Tasks(filename=file.filename, data=file.read(), mark='-', status=status,
                                                   date=date,
                                                   text=text,
                                                   answer='-', fromuser=current_user.name + ' ' + current_user.surname,
                                                   touser=touser,
                                                   header=header,
                                                   fromuserid=current_user.id)
                                    db.session.add(upload)
                                    db.session.commit()
                                    flash(f'Добавлено')
                            else:
                                flash('Неверный формат файла', 'danger')
                        else:
                            flash('Если задание со сроком, введите дату', 'danger')
                    else:
                        flash('Заполните все поля', 'danger')
                else:
                    flash('Этот пользователь не преподаватель', 'danger')
            else:
                flash('Такого пользователя не существует', 'danger')
        except RequestEntityTooLarge:
            flash('Размер файла слишком большой', 'danger')
    return render_template('addtask.html', form=form,
                           statuses=[{'name': 'Задание без срока'}, {'name': 'Задание со сроком'}])


@app.route('/teacher/<id>', methods=['GET', 'POST'])
@login_required
def teacher_check_task(id_teacher):
    user = Users.query.filter_by(id=id_teacher).first()
    task_all = Tasks.query.filter_by(touser=user.email)
    return render_template('teacher_check_task.html', tasks=task_all, user=user, id=int(id_teacher))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route("/login", methods=['GET', 'POST'])
def login():
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
