from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    id = IntegerField()
