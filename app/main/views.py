from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import main
from .. import db
from ..models import User, Permission, Role
from ..email import send_email
from .forms import EditProfileForm

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('SiMianCI.html')

@main.route('/user', methods=['GET', 'POST'])
def user():
    user = current_user
    return render_template('user.html',user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.role = Role.query.get(form.role.data)
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('成功更新您的个人信息')
        return redirect(url_for('.user', user=current_user))
    form.username.data = current_user.username
    form.role.data = current_user.role_id
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, user=current_user)