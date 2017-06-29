# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('登陆邮箱', validators=[Required('请输入邮箱'), Length(1, 64),
                                            Email(message='这好像是个假邮箱...')])
    password = PasswordField('密码', validators=[Required('请输入密码'), Length(6,16,'密码长度为6-16位')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegistrationForm(Form):
    email = StringField('登陆邮箱', validators=[Required(message='请输入邮箱'), Length(1, 64),
                                            Email()])
    username = StringField('用户名', validators=[
        Required(message='请输入用户名'), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                 '用户名仅支持英文喏')])
    password = PasswordField('密码', validators=[
        Required(message='请输入密码'), EqualTo('password2', message='两次输入的密码必须一致！'), Length(6,16,'密码长度为6-16位')])
    password2 = PasswordField('密码确认', validators=[Required(message='请再次输入密码确认')])
    doublecheck = StringField('双向认证口令', validators=[Length(0,64)])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用.')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次输入的密码必须一致！'), Length(6,16,'密码长度为6-16位')])
    password2 = PasswordField('密码确认', validators=[Required()])
    submit = SubmitField('更新密码')


class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[Required(message='请输入邮箱'), Length(1, 64),
                                          Email(message='这好像是个假邮箱...')])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未注册的邮箱！')

class PasswordResetForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email(message='这好像是个假邮箱...')])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次输入的密码必须一致！'), Length(6,16,'密码长度为6-16位')])
    password2 = PasswordField('密码确认', validators=[Required()])
    submit = SubmitField('更新密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未注册的邮箱！')


class ChangeEmailForm(Form):
    email = StringField('新邮箱', validators=[Required('请输入邮箱'), Length(1, 64),
                                                 Email(message='这好像是个假邮箱...')])
    password = PasswordField('密码', validators=[Required('请输入密码')])
    submit = SubmitField('更新邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册.')

class DoubleCheckForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email(message='这好像是个假邮箱...')])
    submit = SubmitField('认证服务器')
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未注册的邮箱！')                                        