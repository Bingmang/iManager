# -*- coding:utf-8 -*-
from flask_wtf import Form
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import iManagerItem


class ItemRegistrationForm(Form):
    item_id = StringField('物品ID', validators=[
                          Required(message='必须输入物品ID'), Length(1, 32)])
    item_name = StringField(
        '物品名称', validators=[Required(message='给物品起个名字吧'), Length(1, 64)])
    angle_range = SelectField('警戒范围', coerce=int)
    submit = SubmitField('注册物品')

    def validate_item_id(self, field):
        if iManagerItem.query.filter_by(item_id=field.data).first():
            raise ValidationError('The ID already been taken.')

    def __init__(self, *args, **kwargs):
        super(ItemRegistrationForm, self).__init__(*args, **kwargs)
        self.angle_range.choices = [(1, '10度以内'), (2, '20度以内'), (3, '30度以内'), 
                            (4, '40度以内'), (5, '50度以内'), (6, '60度以内'), 
                            (7, '70度以内'), (8, '80度以内'), (9, '90度以内')]

class EditItemForm(Form):
    item_id = StringField('物品ID', validators=[
                          Required(message='必须输入物品ID'), Length(1, 32)])
    item_name = StringField('物品名称', validators=[
                          Required(message='给物品起个名字吧'), Length(1, 64)])
    angle_range = SelectField('警戒范围', coerce=int)
    alarm_state = BooleanField('报警状态')
    submit = SubmitField('更改物品')

    def validate_item_id(self, field):
        imanager = iManagerItem.query.filter_by(item_id=field.data).first()
        if imanager and imanager.owner != current_user:
            raise ValidationError('这个ID已经被其他用户注册啦！')

    def __init__(self, item, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.item = item
        self.angle_range.choices = [(1, '10度以内'), (2, '20度以内'), (3, '30度以内'), 
                            (4, '40度以内'), (5, '50度以内'), (6, '60度以内'), 
                            (7, '70度以内'), (8, '80度以内'), (9, '90度以内')]
        
