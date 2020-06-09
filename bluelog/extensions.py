#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""

from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


bootstrap = Bootstrap()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


# 用户加载函数 使current_user能正确返回用户对象
@login_manager.user_loader
def load_user(user_id):
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


# 未登录用户访问使用login_required装饰器的视图时，
# 程序自动重定向到登录视图， 并闪现一个消息提示
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = u'请先登录'
