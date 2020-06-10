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
from bluelog.models import Category, Post, Link, Comment, Reply
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
    return send_from_directory(
        current_app.config['BLUELOG_UPLOAD_PATH'], filename)


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
    pagination = Post.query.order_by(
        Post.timestamp.desc()).paginate(
        page=page,
        per_page=per_page)
    posts = pagination.items
    return render_template(
        'admin/manage_post.html',
        pagination=pagination,
        posts=posts)


@admin_bp.route('/post/change/comment/<int:post_id>', methods=['POST'])
@login_required
def change_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('该文章的评论已关闭', 'danger')
    else:
        post.can_comment = True
        flash('该文章的评论已开启', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/edit/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data
        db.session.commit()
        flash('该文章已经修改成功', 'success')
        return redirect_back()
    form.title.data = post.title
    form.category.data = post.category.id
    form.body.data = post.body
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/delete/post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('您成功删除该篇文章', 'success')
    return redirect_back()


@admin_bp.route('/delete/comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('已删除该条评论', 'success')
    return redirect_back()


@admin_bp.route('/manage/category')
@login_required
def manage_category():
    categories = Category.query.order_by(
        Category.name).filter(
        Category.id != 1).all()
    default = Category.query.get(1)
    return render_template(
        'admin/manage_category.html',
        categories=categories,
        default=default)


@admin_bp.route('/edit/category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryFrom()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('文章类别修改成功!', 'success')
        return redirect(url_for('.manage_category'))
    form.name.data = category.name
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/delete/category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.delete()
    db.session.commit()
    flash('已成功删除该分类,分类下的文章自带添加到 Default 默认分类里!', 'info')
    return redirect_back()


@admin_bp.route('/manage/comment')
@login_required
def manage_comment():
    if request.args.get('filter', 'all') == 'all':
        comment_data = Comment.query
    elif request.args.get('filter') == 'unread':
        comment_data = Comment.query.filter_by(reviewed=False)
    else:
        comment_data = Comment.query.filter_by(from_admin=True)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PRE_PAGE']
    pagination = comment_data.order_by(
        Comment.timestamp.desc()).paginate(
        page=page, per_page=per_page)
    comments = pagination.items
    unread_comment = Comment.query.filter_by(reviewed=False).all()
    return render_template(
        'admin/manage_comment.html',
        comments=comments,
        pagination=pagination,
        unread_comment=unread_comment)


@admin_bp.route('/manage/approve/<int:comment_id>', methods=['POST'])
@login_required
def approve(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.reviewed:
        comment.reviewed = True
    db.session.commit()
    flash('该评论已通过审核', 'success')
    return redirect_back()


@admin_bp.route('/manage/link')
@login_required
def manage_link():
    links = Link.query.order_by(Link.name).all()
    return render_template('admin/manage_link.html', links=links)
