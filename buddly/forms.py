from wtforms import StringField, TextAreaField, validators as v
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed


class EventCreation(Form):
    name = StringField(
        'Name', [
        v.Length(min=1, max=25),
        v.DataRequired()
        ])

    description = TextAreaField(
        'Description/Rules', [
        v.Length(min=1, max=252),
        v.DataRequired()
        ])

    image = FileField(
        'Image', [
        FileAllowed(['gif', 'jpeg', 'jpg', 'png'], 'Images only!')
        ])