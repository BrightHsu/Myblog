#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, HiddenField, PasswordField, BooleanField, SelectField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, Length, Email, URL, Optional
from bluelog.models import Category


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 255)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


class AdminCommentForm(CommentForm):
    name = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 255)])
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.order_by(Category.name).all()]


class CategoryFrom(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()


class LinkFrom(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), Length(1, 255)])
    submit = SubmitField()

