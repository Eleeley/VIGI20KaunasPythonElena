from sqlalchemy.orm import relationship
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)


class NotesCategories(db.Model):
    __tablename__ = 'notes_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_title = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User)


class Notes(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text)
    image = db.Column(db.BLOB)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship(User)
    notes_categories = db.Column(db.Integer, db.ForeignKey('notes_categories.id'))
    note_category = db.relationship(NotesCategories)
