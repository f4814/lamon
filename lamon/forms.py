from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired

from .models import Watcher


class WatcherControlForm(FlaskForm):
    watcherID = SelectField('watcher', validators=[DataRequired()], coerce=int)
    action = SelectField('action', validators=[DataRequired()],
                         choices=[
        ('START', 'start'),
        ('STOP', 'stop'),
        ('RELOAD', 'reload')
    ])

    def update_choices(self):
        self.watcherID.choices = [(g.id, str(g)) for g in Watcher.query.all()]
