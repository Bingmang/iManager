# -*- coding:utf-8 -*-
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager
from .sm3 import sm3

# 不同用户拥有不同权限，此处共分为5级权限


class Permission:
    LEVEL1 = 0x01
    LEVEL2 = 0x02
    LEVEL3 = 0x04
    LEVEL4 = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db .Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            '普通用户': (Permission.LEVEL1 |
                     Permission.LEVEL2 |
                     Permission.LEVEL3, True),
            '管理员': (Permission.LEVEL1 |
                    Permission.LEVEL2 |
                    Permission.LEVEL3 |
                    Permission.LEVEL4, False),
            '网站管理员': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    doublecheck = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    # 用户的记事本
    imanagers = db.relationship(
        'iManagerItem', backref='owner', lazy='dynamic')

    # 初始化用户信息，设置用户权限、头像
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['IMANAGER_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    # 密码不是以明文存储，直接访问password字段是无效的
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 用户密码通过SM3单向杂凑函数进行加密
    @password.setter
    def password(self, password):
        self.password_hash = sm3(password)

    # 验证用户密码的函数，对用户密码的哈希值进行验证（根据输入的密码进行重新哈希）
    def verify_password(self, password):
        return self.password_hash == sm3(password)

    # 生成用户认证token的函数，包含有效期设定
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # 对传进的token进行认证
    def confirm(self, token):
        # 根据当前服务器的密码获取密码校验器
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 根据密码校验器解析token
            data = s.loads(token)
        except:
            # 如果解析失败则返回False
            return False
        #（防止重放攻击）如果从token中解析出的数据中用户id与用户的id不同，则返回False
        if data.get('confirm') != self.id:
            return False
        # 认证成功，更新用户信息
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    # 验证重置密码token的函数
    def reset_password(self, token, new_password):
        # 根据当前服务器的密码获取密码校验器
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 根据密码校验器解析token
            data = s.loads(token)
        except:
            # 如果解析失败则返回false
            return False
        #（防止重放攻击）如果从token中解析出的数据中用户id与要重置的用户的id不同，则返回False
        if data.get('reset') != self.id:
            return False
        # 更新密码，将新数据写入数据库中
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class iManagerItem(db.Model):
    __tablename__ = 'imanagers'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(32), unique=True, index=True)
    item_name = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    alarm_state = db.Column(db.Boolean, default=False)
    registe_time = db.Column(db.DateTime, default=datetime.utcnow)
    angle_range = db.Column(db.Integer, default=1)
