from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import imanager
from .. import db
from ..decorators import admin_required
from ..models import User, Permission, iManagerItem
from ..email import send_email
from .forms import ItemRegistrationForm, EditItemForm


@imanager.route('/itemregistrate', methods=['GET', 'POST'])
@login_required
@admin_required
def itemregistrate():
    form = ItemRegistrationForm()
    if form.validate_on_submit():
        imanager = iManagerItem(item_id=form.item_id.data,
                                 item_name=form.item_name.data,
                                 angle_range=form.angle_range.data,
                                 owner=current_user._get_current_object())
        db.session.add(imanager)
        flash('成功添加 ' + form.item_name.data + ' 到您的记事本中')
        return redirect(url_for('imanager.itemboard'))
    return render_template("imanager/itemregistrate.html", form=form)


@imanager.route('/itemboard', methods=['GET', 'POST'])
@login_required
def itemboard():
    user = current_user
    items = user.imanagers.order_by(iManagerItem.registe_time)
    return render_template('imanager/itemboard.html', user=user, items=items)


@imanager.route('/edit-item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    user = current_user
    item = iManagerItem.query.get_or_404(id)
    if user != item.owner:
        flash('你没有该事件的编辑权限！')
        return redirect(url_for('imanager.itemboard', username=user.username))
    form = EditItemForm(item=item)
    if form.validate_on_submit():
        item.item_id = form.item_id.data
        item.item_name = form.item_name.data
        item.alarm_state = form.alarm_state.data
        item.angle_range = form.angle_range.data
        db.session.add(item)
        flash('成功更新事件信息')
        return redirect(url_for('imanager.itemboard', username=user.username))
    form.item_id.data = item.item_id
    form.item_name.data = item.item_name
    form.alarm_state.data = item.alarm_state
    form.angle_range = item.angle_range
    return render_template('imanager/edit_item.html', form=form)


@imanager.route('/delete-item/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    user = current_user
    item = iManagerItem.query.get_or_404(id)
    if current_user == item.owner:
        db.session.delete(item)
        flash('成功删除事件')
        return redirect(url_for('imanager.itemboard', username=user.username))
    return render_template('.index.html')

