from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired

from .models import Watcher


class WatcherControlForm(FlaskForm):
    watcherID = SelectField('Watcher', validators=[DataRequired()], coerce=int)
    action = SelectField('Action', validators=[DataRequired()],
                         choices=[
        ('START', 'Start'),
        ('STOP', 'Stop'),
        ('RELOAD', 'Reload')
    ])

    def update_choices(self):
        self.watcherID.choices = [(g.id, str(g)) for g in Watcher.query.all()]
