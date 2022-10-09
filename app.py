import os
from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session
from flask_sqlalchemy import SQLAlchemy
from forms.login_form import LoginForm
from forms.note_form import NoteForm
from forms.registration_form import RegistrationForm

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'SecretKeyForProject'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'notes_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from database.database_model import User, Notes, NotesCategories

db.create_all()
db.session.commit()


def check_user(login_session):
    try:
        user_email = login_session["email"]
        user_password = login_session["password"]
        user = User.query.filter_by(email=user_email).first()
        if user.email == user_email and user.password == user_password:
            return user
    except Exception as e:
        return None


def login(form):
    user = User.query.filter_by(email=form.email.data).first()
    if user.email == form.email.data and user.password == form.password.data:
        login_session["user_id"] = user.id
        login_session["email"] = user.email
        login_session["password"] = user.password
        return login_session
    else:
        return None


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "GET":
        form = RegistrationForm()
        return render_template("registration.html", form=form)
    else:
        form = RegistrationForm(request.form)
        if User.query.filter_by(email=form.email.data).first() is None:
            new_user = User(email=form.email.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for("index"))


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "GET":
        user = check_user(login_session)
        if user:
            return redirect(url_for("notes"))
        else:
            form = LoginForm()
            return render_template("index.html", form=form)
    else:
        form = LoginForm(request.form)
        if form.validate_on_submit():
            login(form)
            return redirect(url_for("notes"))


@app.route("/notes", methods=["GET"])
def notes():
    if request.method == "GET":
        user = check_user(login_session)
        if user is not None:
            user_notes = Notes.query.filter_by(user_id=user.id)
            user_categories = NotesCategories.query.filter_by(user_id=user.id)
            return render_template("notes.html", user_notes=user_notes, user_categories=user_categories)
        else:
            return redirect(url_for("index"))


@app.route('/logout', methods=["GET"])
def logout():
    try:
        del login_session["email"]
        del login_session["password"]
        del login_session["user_id"]
        return redirect(url_for("index"))
    except KeyError:
        return redirect(url_for("index"))


@app.route("/addnote", methods=['POST', 'GET'])
def create_note():
    user = check_user(login_session)
    if user:
        if request.method == "POST":
            form = NoteForm(request.form)
            if form.validate_on_submit():
                new_note = Notes(title=form.title.data, text=form.content.data, user_id=user.id,
                                 category_id=form.category_id.data if form.category_id.data else None)
                db.session.add(new_note)
                db.session.commit()
            return redirect(url_for("notes"))


@app.route("/<int:note_id>/editnote/", methods=['POST'])
def edit_notes(note_id):
    user = check_user(login_session)
    if user:
        form = NoteForm(request.form)
        if form.validate_on_submit():
            note_to_edit = Notes.query.get_or_404(note_id)
            note_to_edit.title = form.title.data
            note_to_edit.text = form.content.data
            note_to_edit.category_id = form.category_id.data if form.category_id.data else None
            note_to_edit.image = form.image.data
            db.session.add(note_to_edit)
            db.session.commit()
    return redirect(url_for("notes"))


@app.route("/<int:note_id>/addcategory/", methods=['POST'])
def add_category(note_id):
    user = check_user(login_session)
    if user:
        form = NoteForm(request.form)
        if form.validate_on_submit():
            note_to_edit = Notes.query.get_or_404(note_id)
            note_to_edit.category_id = form.category_id.data if form.category_id.data else None
            db.session.add(note_to_edit)
            db.session.commit()
    return redirect(url_for("notes"))


if __name__ == '__main__':
    app.run()
