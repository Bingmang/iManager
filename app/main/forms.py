# -*- coding:utf-8 -*-
from flask_wtf import Form
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User,Role

class EditProfileForm(Form):
    username = StringField('用户名', validators=[
        Required(message='请输入用户名'), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'用户名仅支持英文喏')])
    role = SelectField('用户权限', coerce=int)
    location = StringField('所在地', validators=[Length(0,64)])
    about_me = StringField('关于我', validators=[Length(0,64)])
    doublecheck = StringField('双向认证口令', validators=[Length(0,64)])
    submit = SubmitField('更新信息')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user and user != current_user:
            raise ValidationError('这个用户名已经被其他用户注册啦！')