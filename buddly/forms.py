from wtforms import StringField, TextAreaField, IntegerField, validators as v
from flask_wtf import Form as FlaskForm
from flask_wtf.file import FileField, FileAllowed


class BuddyCreation(FlaskForm):
    name = StringField(
        'Name', [
            v.Length(min=1, max=63),
            v.DataRequired()
        ])

    email = StringField(
        'Email', [
            v.Email(),
            v.Length(min=1, max=255),
            v.DataRequired()
        ])

class BuddyProfile(FlaskForm):
    name = StringField(
        'Name', [
            v.Length(min=1, max=63),
            v.DataRequired()
        ])

    email = StringField(
        'Email', [
            v.Email(),
            v.Length(min=1, max=255),
            v.DataRequired()
        ])

    bio = TextAreaField(
        'Bio', [
            v.Length(min=0, max=1024)
        ]
    )

class EventBuddies(FlaskForm):
    name = StringField(
        'Name', [
            v.Length(min=1, max=63),
            v.DataRequired()
        ])

    email = StringField(
        'Email', [
            v.Email(),
            v.Length(min=1, max=255),
            v.DataRequired()
        ])


class EventCreation(FlaskForm):
    name = StringField(
        'Name', [
            v.Length(min=1, max=63),
            v.DataRequired()
        ])

    description = TextAreaField(
        'Description/Rules', [
            v.Length(min=1, max=255),
            v.DataRequired()
        ])

    image = FileField(
        'Image', [
            FileAllowed(['gif', 'jpeg', 'jpg', 'png'], 'Images only!')
        ])

    num_buddies = IntegerField(
        'Buddies per Santa',
        [
            v.NumberRange(min=1)
        ],
        default=1
    )
