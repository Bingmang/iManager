# -*- coding:utf-8 -*-
from flask_wtf import Form
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import iManagerItem


class ItemRegistrationForm(Form):
    item_id = StringField('事件名称', validators=[
                          Required(message='请输入事件名称'), Length(1, 32)])
    item_name = StringField(
        '事件内容', validators=[Required(message='请输入事件内容'), Length(1, 64)])
    angle_range = SelectField('优先级', coerce=int)
    submit = SubmitField('提交事件')

    def validate_item_id(self, field):
        if iManagerItem.query.filter_by(item_id=field.data).first():
            raise ValidationError('该事件名称被其他人注册啦！')

    def __init__(self, *args, **kwargs):
        super(ItemRegistrationForm, self).__init__(*args, **kwargs)
        self.angle_range.choices = [(1, '优先级1'), (2, '优先级2'), (3, '优先级3'), 
                            (4, '优先级4'), (5, '优先级5')]

class EditItemForm(Form):
    item_id = StringField('物品ID', validators=[
                          Required(message='请输入事件名称'), Length(1, 32)])
    item_name = StringField('物品名称', validators=[
                          Required(message='请输入事件内容'), Length(1, 64)])
    angle_range = SelectField('警戒范围', coerce=int)
    alarm_state = BooleanField('事件已完成')
    submit = SubmitField('提交事件')

    def validate_item_id(self, field):
        imanager = iManagerItem.query.filter_by(item_id=field.data).first()
        if imanager and imanager.owner != current_user:
            raise ValidationError('该事件名称被其他人注册啦！')

    def __init__(self, item, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.item = item
        self.angle_range.choices = [(1, '优先级1'), (2, '优先级2'), (3, '优先级3'), 
                            (4, '优先级4'), (5, '优先级5')]
        
