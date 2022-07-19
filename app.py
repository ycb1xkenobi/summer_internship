from flask import render_template, url_for, request, redirect, flash, send_file
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash
from io import BytesIO
from forms import LoginForm, AddTask, ChangePassword, Registration, UpdateAccountForm, RegisterPage, DashboardView, Users, AddStudentForm, DeleteStudentForm
from models import Tasks, AddStudent
from passwords import create_password
from save_picture import save_picture
from __init__ import db, app, manager



@app.route('/')
@login_required
def index():
    return render_template("index.html")


@app.route('/admin/registerpage/', methods=['POST', 'GET'])
def register():
    form = Registration()
    if form.validate_on_submit():
        email = request.form.get('email')
        role = request.form.get('select')
        non_hashed_password = create_password()
        password = generate_password_hash(non_hashed_password)
        userinfo = Users(email=email, password=password, role=role, name='-', surname='-', yearadmission='-',
                         group='-')
        if role in app.config['ROLES']:
            user = Users.query.filter_by(email=email).first()
            if user:
                flash('Такой пользователь уже зарегистрирован', 'danger')
            else:
                if '@' in email:
                    db.session.add(userinfo)
                    db.session.commit()
                    flash(f'Пароль {non_hashed_password} для пользователя {email}', 'success')
                else:
                    flash('Это не почта!', 'danger')
        else:
            flash('Такой роли не существует', 'danger')
    return render_template("register.html", form=form)


@app.route("/teacher/checktask/<task_id>", methods=['GET', 'POST'])
@login_required
def teacher_check_task_id(task_id):
    task_id = int(task_id)
    checked_task = Tasks.query.filter_by(id=task_id).first()
    if request.method == 'POST':
        checked_task.mark = request.form.get("selectmark")
        checked_task.status = request.form.get("selectstatus")
        checked_task.answer = request.form.get("answer")
        db.session.commit()
        return redirect('/teacher')
    return render_template('teacher_check_task_id.html', task=checked_task)

@app.route("/student/checktask/<task_id>")
@login_required
def student_check_task_id(task_id):
    check_my_id = current_user.id
    checked_task = Tasks.query.filter_by(id=task_id).first()
    return render_template('student_check_task_id.html', task=checked_task, id=str(check_my_id))

@app.route("/student/deletetask/<task_id>")
@login_required
def delete_task(task_id):
    try:
        delete_task = Tasks.query.filter_by(id=task_id).first()
        if current_user.id == int(delete_task.fromuserid):
            db.session.delete(delete_task)
            db.session.commit()
            flash('Вы успешно удалили задание', 'success')
        else:
            flash('Вы не создавали это задание', 'danger')
    except AttributeError:
        flash('Такого задания не существует', 'danger')
    return render_template('delete_task.html')


@app.route('/student/uptask/<task_id>')
@login_required
def up_task(task_id):
    up_task = Tasks.query.filter_by(id=task_id).first()
    priority_up = up_task.priority

    if current_user.id == int(up_task.fromuserid):
        while priority_up != 0:
            changetask = Tasks.query.filter_by(priority=priority_up).first()
            if changetask:
                changetask.priority = priority_up+1
                db.session.commit()
            priority_up -= 1
        up_task.priority = 1
        db.session.commit()
        flash('Вы успешно подняли ваше задание', 'success')
    else:
        flash('Вы не создавали это задание', 'danger')
    return render_template('uptask.html')


@app.route('/download/<task_id>')
@login_required
def download(task_id):
    task = Tasks.query.filter_by(id=task_id).first()
    try:
        if current_user.id == int(task.fromuserid):
            return send_file(BytesIO(task.data), attachment_filename=task.filename, as_attachment=True)
        elif current_user.email == task.touser:
            return send_file(BytesIO(task.data), attachment_filename=task.filename, as_attachment=True)
        else:
            return 'Вы не загружали этот файл/Этот файл не для вас'
    except TypeError:
        return 'Такого файла не существует'
    except AttributeError:
        return 'Такого задания не существует'




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
        if current_user.role == 'Преподаватель':
            current_user.group = '-'
            current_user.yearadmission = '-'
        else:
            current_user.group = form.group.data
            current_user.yearadmission = form.yearadmission.data
        db.session.commit()
        flash('Вы обновили свой аккаунт!', 'success')
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
            non_hashed_password = form.password1.data
            password = generate_password_hash(non_hashed_password)
            current_user.password = password
            db.session.commit()
            flash('Пароль обновлен', 'success')
        else:
            flash('Пароли не совпадают', 'danger')
    return render_template('changepassword.html', form=form)


@app.route("/teacher/addstudent", methods=['GET', 'POST'])
@login_required
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        teacherid = str(current_user.id)
        student = form.studentemail.data
        user = Users.query.filter_by(email=student).first()
        if user:
            info = AddStudent(studentemail=student, teacherid=teacherid, studentid=str(user.id))
            db.session.add(info)
            db.session.commit()
            flash(f'Вы успешно добавили студента {user.name} {user.surname}', 'success')
        else:
            flash('Такого студента не существует','danger')
    return render_template('addstudent.html', form=form)


@app.route("/teacher/deletestudent", methods=['GET', 'POST'])
@login_required
def delete_student():
    form = DeleteStudentForm()
    if form.validate_on_submit():
        teacherid = str(current_user.id)
        student = form.studentemail.data
        user = Users.query.filter_by(email=student).first()
        if user:
            info1 = AddStudent.query.filter_by(teacherid=teacherid).first()
            if info1:
                info2 = info1.query.filter_by(studentemail=student).first()
                if info2:
                    db.session.delete(info2)
                    db.session.commit()
                    flash(f'Вы успешно удалили студента {user.name} {user.surname}', 'success')
                else:
                    flash('Такой студент у вас не добавлен', 'danger')
            else:
                flash('Вы еще не добавляли студентов','danger')
        else:
            flash('Такого студента не существует','danger')
    return render_template('addstudent.html', form=form)


@app.route("/teacher/mystudents")
@login_required
def mystudents():
    myid = str(current_user.id)
    mystudent = AddStudent.query.filter_by(teacherid=myid).all()
    return render_template('mystudents.html', students=mystudent)


app.route("/account/<id_profile>", methods=['GET', 'POST'])
@login_required
def watch_profiles(id_profile):
    user = Users.query.filter_by(id=id_profile).first()
    if user:
        image_file = url_for('static', filename='profile_pics/' + user.image_file)
        return render_template('profile.html', user=user, image_file=image_file)

@app.route('/teacher/checkedtask/<id>')
@login_required
def teacher_checked_task(id):
    user = Users.query.filter_by(id=id).first()
    task_all = Tasks.query.filter_by(touser=user.email)
    return render_template('teacher_checked_task.html', tasks=task_all, user=user, id=int(id))

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
        task = db.session.query(Tasks).order_by(Tasks.priority.desc()).first()
        if task:
            priority = task.priority + 1
        else:
            priority = 1
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
                            currentemail = str(current_user.email)
                            teacherid = str(user.id)
                            check1 = AddStudent.query.filter_by(teacherid=teacherid).first()
                            if check1:
                                check2 = check1.query.filter_by(studentemail=currentemail).first()
                                if check2:
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
                                                   fromuserid=current_user.id,
                                                   priority=priority)
                                            db.session.add(upload)
                                            db.session.commit()
                                            flash(f'Добавлено', 'success')
                                    else:
                                        flash('Неверный формат файла', 'danger')
                            else:
                                flash('Данный преподаватель вас не добавил', 'danger')
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


@app.route('/student/uploads/<id_student>')
@login_required
def check_my_upload_task(id_student):
    uploaded_task = Tasks.query.filter_by(fromuserid=str(current_user.id))
    return render_template('student_all_tasks.html', id=int(id_student), uploaded=uploaded_task)


@app.route('/teacher')
@login_required
def teacher():
    return render_template('teacher.html')


@app.route('/teacher/<id_teacher>', methods=['GET', 'POST'])
@login_required
def teacher_check_task(id_teacher):
    user = Users.query.filter_by(id=id_teacher).first()
    task_all = Tasks.query.filter_by(touser=user.email).order_by(Tasks.priority).all()
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
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            user = Users.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.password, password):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect('/')
            else:
                flash('Неудачный вход', 'danger')
        else:
            flash('Заполните все поля', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)

    return response


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


admin = Admin(app, 'Админ панель', template_mode='bootstrap3', index_view=DashboardView(), endpoint='admin')
admin.add_view(ModelView(Users, db.session, name='Пользователи'))
admin.add_view(ModelView(Tasks, db.session, name='Задания'))
admin.add_view(ModelView(AddStudent, db.session, name='Студенты-преподы'))
admin.add_view(RegisterPage(name='Регистрация пользователей'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)