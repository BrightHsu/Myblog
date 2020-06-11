#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response
from flask import current_app
from bluelog.models import Post, Comment, Reply, Category
from bluelog.utils import redirect_back
from bluelog.forms import CommentForm, AdminCommentForm
from flask_login import current_user
from bluelog.extensions import db
from bluelog.emails import send_new_comment_email, send_new_reply_email

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(
        Post.timestamp.desc()).paginate(
        page, per_page)
    posts = pagination.items
    return render_template(
        'blog/index.html',
        pagination=pagination,
        posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/change/<path:theme>')
def change_theme(theme):
    response = make_response(redirect_back())
    response.set_cookie('theme', theme, max_age=30 * 24 * 60 * 60)
    return response


@blog_bp.route('/show/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PRE_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(
        reviewed=True) .order_by(
        Comment.timestamp.asc()).paginate(
            page=page,
        per_page=per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.name.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        reviewed = True
        from_admin = True
    else:
        form = CommentForm()
        reviewed = False
        from_admin = False

    if form.validate_on_submit():
        author = form.name.data
        email = form.email.data
        site = form.site.data
        body = form.comment.data

        comment = Comment(
            author=author,
            email=email,
            site=site,
            body=body,
            reviewed=reviewed,
            from_admin=from_admin,
            post=post)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:
            flash('您的评论已发送', 'success')
        else:
            flash('感谢您的评论, 该评论需要通过审核后才能显示', 'info')
            send_new_comment_email(post) # 发送提醒邮件给管理员

        return redirect(url_for('.show_post', post_id=post.id))

    return render_template(
        'blog/post.html',
        post=post,
        comments=comments,
        pagination=pagination,
        form=form)


@blog_bp.route('/reply/form/<int:comment_id>', methods=['POST'])
def reply_form(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.name.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        # reviewed = True
        from_admin = True
    else:
        form = CommentForm()
        # reviewed = False
        from_admin = False

    if form.validate_on_submit():
        author = form.name.data
        email = form.email.data
        site = form.site.data
        body = form.comment.data
        reply = Reply(author=author, email=email, site=site, body=body, from_admin=from_admin,
                      comment=comment)
        db.session.add(reply)
        db.session.commit()
        flash('您的评论已发送', 'success')
        send_new_reply_email(comment)  # 发送提醒邮件给评论人
        return redirect(url_for('.show_post', post_id=comment.post_id))
    return redirect_back()


@blog_bp.route('/show/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(
        Post.timestamp.desc()).paginate(
        page=page, per_page=per_page)
    posts = pagination.items
    return render_template(
        'blog/category.html',
        category=category,
        pagination=pagination,
        posts=posts)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    r_id = request.args.get('next')
    page = request.args.get('page')
    if not comment.post.can_comment:
        flash('评论已关闭, 无法进行评论', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for(
            '.show_post',
            post_id=comment.post_id,
            reply=comment_id,
            author=comment.author,
            r_id=r_id,
            page=page,
            admin=comment.from_admin) +
        '#comment-form')
