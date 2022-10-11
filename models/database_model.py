from sqlalchemy.orm import relationship
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)

association_table = db.Table(
    "notes_categories",
    db.metadata,
    db.Column("notes_id", db.ForeignKey("notes.id"), primary_key=True),
    db.Column("category_id", db.ForeignKey("categories.id"), primary_key=True),
)


class Notes(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    image = db.Column(db.BLOB)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship(User)
    categories = relationship(
        "Categories", secondary=association_table, back_populates="notes"
    )


class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_title = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship(User)
    notes = relationship(
        "Notes", secondary=association_table, back_populates="categories"
    )
