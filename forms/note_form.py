from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField
from wtforms.validators import DataRequired


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    id = IntegerField()
    content = StringField("Note", )
    image = FileField('Image upload')
    category_id = IntegerField()
