#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""


import os
import click
from flask import Flask, request, render_template
from bluelog.settings import config
from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import bootstrap, ckeditor, mail, moment, db, login_manager, csrf
from bluelog.models import Admin, Category, Link, Post, Comment, Reply
from flask_login import current_user


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_blueprint(app)  # 注册篮本
    register_extensions(app)    # 注册扩展
    register_shell_context(app)     # 注册shell上下文
    register_template_context(app)  # 注册模板上下文
    register_errors(app)    # 注册错误页
    register_commands(app)  # 注册shell命令
    register_template_filter(app)  # 注册模板filter

    return app


def register_blueprint(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_extensions(app):
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    @app.context_processor
    def make_context_template():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()

        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count() + \
                              Reply.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin,
            categories=categories,
            links=links,
            unread_comments=unread_comments
        )


def register_template_filter(app):
    @app.template_filter()
    def _replies(comment):
        replies = Reply.query.with_parent(comment).filter_by(reviewed=True).all()
        return replies

    @app.template_filter()
    def reviewed(comments):
        num = 0
        for comment in comments:
            if comment.reviewed:
                num += 1
        return num

    @app.template_filter()
    def reply_sort(replys):
        return sorted(replys, key=lambda x: x.timestamp, reverse=False)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', hide_input=True, prompt=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Bluelog just for you."""
        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)
        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    @click.option('--reply', default=200, help='Quantity of reply, default is 200')
    def forge(category, post, comment, reply):
        """Generates the fake categories, posts, and comments."""
        from bluelog.fakes import fake_categories, fake_posts, fake_comments, fake_reply, fake_admin, fake_link

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)
        click.echo('Generating %d comments... '% comment)
        fake_comments(comment)
        click.echo('Generating %d reply...' % reply)
        fake_reply(reply)

        click.echo('Generating the links')
        fake_link()

        click.echo('Done.')

