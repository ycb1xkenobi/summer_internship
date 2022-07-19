from flask import render_template
from flask_admin import BaseView, expose, AdminIndexView
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import ValidationError
from models import Users


class UploadSomething(FlaskForm):
    submit = SubmitField('Сохранить')

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


class Registration(FlaskForm):
    email = StringField('Введите почту')
    submit = SubmitField('Регистрация')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Эта почта занята')

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


class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/dashboard_index.html')