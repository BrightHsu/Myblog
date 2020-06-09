#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""

from flask import Blueprint, url_for, flash, request, redirect, current_app, render_template, send_from_directory
from bluelog.utils import redirect_back, allowed_file
from flask_login import current_user, login_required
from bluelog.forms import PostForm, CategoryFrom, LinkFrom
from bluelog.models import Category, Post, Link
from flask_ckeditor import upload_success, upload_fail
import os
from bluelog.extensions import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/new/post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        category = Category.query.get(form.category.data)
        body = form.body.data
        post = Post(
                title=title,
                category=category,
                body=body
            )
        db.session.add(post)
        db.session.commit()
        flash('恭喜您完成了一篇新文章!', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['BLUELOG_UPLOAD_PATH'], filename)


@admin_bp.route('/upload/image', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('只能是图片格式!')
    f.save(os.path.join(current_app.config['BLUELOG_UPLOAD_PATH'], f.filename))
    url = url_for('.get_image', filename=f.filename)
    return upload_success(url, f.filename)


@admin_bp.route('/new/category')
@login_required
def new_category():
    form = CategoryFrom()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('您成功新建一个分类!', 'success')
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/new/link')
@login_required
def new_link():
    form = LinkFrom()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        category = Category(name=name, url=url)
        db.session.add(category)
        db.session.commit()
        flash('您成功新建一条链接!', 'success')

    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/manage/post')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_POST_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts)