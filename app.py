import os
from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session
from flask_sqlalchemy import SQLAlchemy
from forms.login_form import LoginForm
from forms.note_form import NoteForm
from forms.registration_form import RegistrationForm
from forms.category_form import CategoryForm

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'SecretKeyForProject'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'notes_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import User, Notes, Categories

with app.app_context():
    db.create_all()
    db.session.commit()


@app.context_processor
def user_note_and_categories():
    try:
        user_notes = Notes.query.filter_by(user_id=login_session["user_id"])
        user_categories = Categories.query.filter_by(user_id=login_session["user_id"])
    except KeyError:
        user_notes = []
        user_categories = []

    return {"user_notes": user_notes, "user_categories": user_categories}


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
    if user:
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
            create_note_form = NoteForm()
            create_category_form = CategoryForm()
            return redirect(
                url_for("notes", create_note_form=create_note_form, create_category_form=create_category_form))
        else:
            form = LoginForm()
            return render_template("index.html", form=form)
    else:
        form = LoginForm(request.form)
        if form.validate_on_submit():
            login(form)
            create_note_form = NoteForm()
            create_category_form = CategoryForm()
            return redirect(
                url_for("notes", create_note_form=create_note_form, create_category_form=create_category_form))


@app.route("/notes", methods=["GET"])
def notes():
    if request.method == "GET":
        user = check_user(login_session)
        if user is not None:
            user_notes = Notes.query.filter_by(user_id=user.id)
            user_categories = Categories.query.filter_by(user_id=user.id)
            create_note_form = NoteForm()
            return render_template("notes.html", user_notes=user_notes, user_categories=user_categories,
                                   create_note_form=create_note_form)
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


@app.route("/addnote", methods=['POST'])
def create_note():
    user = check_user(login_session)
    if user:
        if request.method == "POST":
            form = NoteForm(request.form)
            if form.validate_on_submit():
                new_note = Notes(title=form.title.data, content=form.content.data,
                                 image=bytes(form.image.data, "utf-8"), user_id=user.id)
                db.session.add(new_note)
                db.session.commit()
            create_note_form = NoteForm()
            create_category_form = CategoryForm()
            return redirect(
                url_for("notes", create_note_form=create_note_form, create_category_form=create_category_form))


@app.route("/addcategory", methods=['POST'])
def create_category():
    user = check_user(login_session)
    if user:
        if request.method == "POST":
            form = CategoryForm(request.form)
            if form.validate_on_submit():
                new_category = Categories(category_title=form.title.data, user_id=user.id)
                db.session.add(new_category)
                db.session.commit()
            create_note_form = NoteForm()
            create_category_form = CategoryForm()
            return redirect(
                url_for("category_list", create_note_form=create_note_form, create_category_form=create_category_form))


@app.route("/categories", methods=['GET'])
def category_list():
    user = check_user(login_session)
    if user:
        if request.method == "GET":
            category_list = Categories.query.filter_by(user_id=user.id).all()
            create_note_form = NoteForm()
            create_category_form = CategoryForm()
            return render_template("categories.html", category_list=category_list, create_note_form=create_note_form,
                                   create_category_form=create_category_form)


@app.route("/editcategory/<int:category_id>/", methods=['POST', 'GET'])
def edit_category(category_id):
    if request.method == "POST":
        user = check_user(login_session)
        if user:
            form = CategoryForm(request.form)
            if form.validate_on_submit():
                category_to_edit = Categories.query.get_or_404(category_id)
                category_to_edit.category_title = form.title.data
                db.session.add(category_to_edit)
                db.session.commit()
    else:
        category = Categories.query.get_or_404(category_id)
        form = CategoryForm()
        form.id.data = category.id
        form.title.data = category.category_title
        user_categories = Categories.query.filter_by(user_id=login_session["user_id"]).all()
        return render_template("edit_category.html", form=form, category_id=category_id,
                               user_categories=user_categories)
    create_note_form = NoteForm()
    create_category_form = CategoryForm()
    user_categories = Categories.query.filter_by(user_id=login_session["user_id"]).all()
    return redirect(
        url_for("category_list", create_note_form=create_note_form, create_category_form=create_category_form,
                user_categories=user_categories))


@app.route("/editnote/<int:note_id>/", methods=['POST', 'GET'])
def edit_notes(note_id):
    if request.method == "POST":
        user = check_user(login_session)
        if user:
            form = NoteForm(request.form)
            if form.validate_on_submit():
                note_to_edit = Notes.query.get_or_404(note_id)
                note_to_edit.title = form.title.data
                note_to_edit.content = form.content.data
                note_to_edit.image = bytes(form.image.data, "utf-8")
                try:
                    categories = Categories.query.get_or_404(form.category_id.data)
                    note_to_edit.categories.append(categories)
                except Exception:
                    pass
                db.session.add(note_to_edit)
                db.session.commit()
    else:
        notes = Notes.query.get_or_404(note_id)
        form = NoteForm()
        form.id.data = notes.id
        form.title.data = notes.title
        form.content.data = notes.content
        form.image.data = notes.image
        form.category_id.data = notes.categories
        user_categories = Categories.query.filter_by(user_id=login_session["user_id"]).all()
        return render_template("edit_note.html", form=form, note_id=note_id, user_categories=user_categories)
    create_note_form = NoteForm()
    create_category_form = CategoryForm()
    return redirect(url_for("notes", create_note_form=create_note_form, create_category_form=create_category_form))


if __name__ == '__main__':
    app.run()

