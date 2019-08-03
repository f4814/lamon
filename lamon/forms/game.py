from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import DataRequired, Optional

class CreateUpdateForm(FlaskForm):
    name = TextField('Name', validators=[DataRequired()])
