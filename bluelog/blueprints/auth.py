#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""

from flask import Blueprint, render_template, flash
from flask_login import current_user, login_required, login_user, logout_user
from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_back()

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('欢迎回来！', 'success')
                return redirect_back()

            flash('您的用户名或者密码有误，请重新输入!', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出登录!', 'info')
    return redirect_back()
