#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @Time    : 2020/6/1 11:42
    @Author  : David Ben
    @FileName: __init__.py.py
    @Email: hsudavid@163.com
    @Software: PyCharm
"""

from faker import Faker
import random
from sqlalchemy.exc import IntegrityError
from bluelog.models import Admin, Category, Post, Comment, Reply, Link
from bluelog.extensions import db

fake = Faker('zh_CN')  # 无参数，默认英文，zh_CN指定为中文


def fake_admin():
    admin = Admin(
        username='admin',
        name='刘伯温',
        bluelog_title='Bluelog',
        bluelog_sub_title="No, I'm the real thing.",
        about='Um, l, Mima Kirigoe, had a fun time as a member of CHAM...'
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):

    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员发表的评论
        comment = Comment(
            author='刘伯温',
            email='mima@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            from_admin=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_reply(count=200):
    for i in range(count):
        reply = Reply(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            comment=Comment.query.get(random.randint(1, Comment.query.count()))
        )
        db.session.add(reply)

    salt = int(count * 0.5)
    for i in range(salt):
        # 未审核评论
        reply = Reply(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            comment=Comment.query.get(random.randint(1, Comment.query.count()))
        )
        db.session.add(reply)

        # 管理员发表的评论
        reply = Reply(
            author='刘伯温',
            email='mima@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            from_admin=True,
            comment=Comment.query.get(random.randint(1, Comment.query.count()))
        )
        db.session.add(reply)
    db.session.commit()


def fake_link():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()

