from flask_wtf import FlaskForm
from wtforms import (HiddenField, TextField, FieldList, IntegerField, FormField,
                     SubmitField, SelectField)
from wtforms.validators import DataRequired, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class ControlForm(FlaskForm):
    """ Form used to control a watcher. """
    reload = SubmitField('reload')
    start = SubmitField('start')
    stop = SubmitField('stop')


class CreateForm(FlaskForm):
    """ Form used to select which thread_class the newly created watcher will
    use
    """
    watcher_class = SelectField('Watcher Class', validators=[DataRequired()],
                                choices=[
        ('lamon.watcher.plugin.source_engine.SourceEngineWatcher',
         'Source Engine Watcher'),
        ('lamon.watcher.plugin.quake3.Quake3Watcher',
         'Quake3 Watcher'),
        ('tests.test_watcher.fake.FakeWatcher',
         'Fake Watcher')
    ])


class EditForm(FlaskForm):
    """ Form used to edit a watcher instance """
    game = QuerySelectField(allow_blank=True)

    @classmethod
    def load_config(cls, watcher_class, watcher_model):
        """ Prepare form for a specific watcher """
        cls.watcher = watcher_class
        cls.game = QuerySelectField(
            allow_blank=True, default=watcher_model.game)

        for key, opts in watcher_class.config_keys.items():
            value = None

            for i in watcher_model.config:
                if i.key == key:
                    value = i.value

            if watcher_class.config_keys[key]['type'] is int:
                field = IntegerField
            else:
                field = TextField

            if watcher_class.config_keys[key]['required']:
                validators = [DataRequired()]
            else:
                validators = [Optional()]

            setattr(cls, key, field(key, default=value, validators=validators))

        return cls
