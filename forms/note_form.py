from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, SelectField
from wtforms.validators import DataRequired


class NonValidatingSelectField(SelectField):
    """
    Attempt to make an open ended select multiple field that can accept dynamic
    choices added by the browser.
    """

    def pre_validate(self, form):
        pass

class NoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    id = IntegerField()
    content = StringField("Note", validators=[])
    image = FileField(validators=[])
    category_id = NonValidatingSelectField("Categories", validators=[])
