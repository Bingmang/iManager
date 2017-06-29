from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User, Permission
from ..email import send_email

# 从auth目录下的forms.py中获取各种表单
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, DoubleCheckForm

# 在用户请求前，始终要确认用户的认证信息，保证是有效用户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:  # 如果当前用户已登陆
        current_user.ping()  # 更新用户最后一次登陆的时间
        # 如果用户没有认证，则跳转到未认证界面
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

<<<<<<< HEAD
#/login路由，对用户进行双向认证
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:   #如果当前用户已登陆
        return redirect(url_for('main.user'))   #返回到用户界面
    form = DoubleCheckForm() #获取双向认证的表单
    if form.validate_on_submit():   #处理表单提交事件
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            return render_template("auth/_doublecheck.html", user=user)
    return render_template("auth/doublecheck.html", form=form)

# 双向认证登陆界面
@auth.route('/doublecheck', methods=['GET', 'POST'])
def doublecheck():
    if current_user.is_authenticated:   #如果当前用户已登陆
        return redirect(url_for('main.user'))   #返回到用户界面
    form = LoginForm()  #获取登陆表单
    if form.validate_on_submit():   #处理表单提交事件
        user = User.query.filter_by(email=form.email.data).first()  #根据email查询用户
        if user is not None and user.verify_password(form.password.data):   #如果查询到该用户并且验证密码成功
            login_user(user, form.remember_me.data) #登陆该用户
            return redirect(request.args.get('next') or url_for('main.user'))  #重定向到另一个页面
        flash('帐号密码错误，请重试。')    #否则提示用户帐号密码错误
    return render_template('auth/login.html', form=form)    #回到该页面，并将表单中的数据保留
    if current_user.is_authenticated:   #如果当前用户已登陆
        return redirect(url_for('main.user'))   #返回到用户界面
=======
# /login路由，处理用户登陆界面
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 获取登陆表单
    if form.validate_on_submit():  # 处理表单提交事件
        user = User.query.filter_by(
            email=form.email.data).first()  # 根据email查询用户
        # 如果查询到该用户并且验证密码成功
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)  # 登陆该用户
            # 重定向到另一个页面
            return redirect(request.args.get('next') or url_for('main.user'))
        flash('帐号密码错误，请重试。')  # 否则提示用户帐号密码错误
    return render_template('auth/login.html', form=form)  # 回到该页面，并将表单中的数据保留
>>>>>>> 261682909a596851ad7bcdd749f8e98e95c7e540

# /logout路由，处理用户登出事件
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出.')
    return redirect(url_for('auth.login'))

# /register路由，处理用户注册事件
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # 获取注册表单（输入处理在forms.py中定义了）
    if form.validate_on_submit():  # 处理表单提交事件
        # 注册的时候会将传入的密码自动通过哈希函数加密并存储在数据库中
        user = User(email=form.email.data,
                    username=form.username.data,
<<<<<<< HEAD
                    password=form.password.data,
                    doublecheck=form.doublecheck.data)    
        db.session.add(user)    #将user注册到数据库中
        db.session.commit()     #提交数据
=======
                    password=form.password.data)
        db.session.add(user)  # 将user注册到数据库中
        db.session.commit()  # 提交数据
>>>>>>> 261682909a596851ad7bcdd749f8e98e95c7e540
        token = user.generate_confirmation_token() #生成token
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('一封认证邮件已经发送到您的邮箱。')
        return redirect(url_for('auth.login'))  # 注册完毕后跳转到登陆界面
    # 否则返回该界面，并保留表单中的数据
    return render_template('auth/register.html', form=form)

# /confirm路由，处理注册时根据token为用户注册帐号的事件
@auth.route('/confirm/<token>')
@login_required
def confirm(token):  # 分析传进的参数token
    if current_user.confirmed:  # 如果用户已经注册认证过了，则返回到登陆界面
        return redirect(url_for('auth.login'))
    if current_user.confirm(token):  # 如果token有效，则告知用户认证成功
        flash('您已成功认证，感谢注册Simian CI！')
    else:
        flash('您的认证链接无效或已使用，请确认！')
    return redirect(url_for('auth.login'))  # 认证无效，返回到登陆界面

# /change-password路由，处理更改密码的事件
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()  # 获取更改密码的表单
    if form.validate_on_submit():  # 处理表单提交事件
        if current_user.verify_password(form.old_password.data):  # 如果旧密码与当前用户密码一致
            current_user.password = form.password.data  # 更新用户密码
            db.session.add(current_user)  # 更新用户信息
            flash('您的密码已更新。')
            return redirect(url_for('main.user'))  # 返回至登陆界面
        else:
            flash('密码错误，请检查。')
    return render_template("auth/change_password.html", form=form)

# /reset路由，处理重置密码的事件
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:  # 如果当前用户是匿名用户
        return redirect(url_for('auth.register'))  # 则返回至注册界面
    form = PasswordResetRequestForm()  # 获取重置密码的表单
    if form.validate_on_submit():  # 处理表单提交事件
        user = User.query.filter_by(email=form.email.data).first()  # 在数据库中查询用户
        if user is not None:  # 查询到用户
            token = user.generate_reset_token()  # 生成token用于验证
            # 将token通过邮箱发送给该用户的注册邮箱
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('一封重置密码的确认邮件已发送至您的邮箱。')  # 提示用户已发送邮箱
        return redirect(url_for('auth.login'))  # 返回至登陆界面
    return render_template('auth/reset_password.html', form=form)

# /reset/TOKEN路由，用于验证重置密码的token
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:  # 如果当前用户是匿名用户，则重定向到注册界面
        return redirect(url_for('auth.login'))
    form = PasswordResetForm()  # 获取重置密码的表单
    if form.validate_on_submit():  # 处理表单提交事件
        user = User.query.filter_by(
            email=form.email.data).first()  # 从数据库中查询到该用户
        # （防止伪造攻击）如果没有查询到用户，直接返回主页
        if user is None:
            return redirect(url_for('main.index'))
        # 如果token有效，则更新密码
        if user.reset_password(token, form.password.data):
            flash('您的密码已更新。')
            return redirect(url_for('auth.login'))  # 返回登陆界面
        else:
            return redirect(url_for('main.index'))  # token无效，直接返回主页
    return render_template('auth/reset_password.html', form=form)

# /change-email路由，用于更改用户的邮箱
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            # 生成token，并通过邮件发送给用户
            send_email(new_email, '认证您的新邮箱',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封确认邮箱已发送至您的新邮箱。')
            return redirect(url_for('auth.login'))
        else:
            flash('邮箱或密码无效，请检查。')
    return render_template("auth/change_email.html", form=form)

# /change-email/token路由，用户验证更改邮箱的token
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('您的邮箱已更新。')
    else:
        # （防止伪造攻击）token无效
        flash('无效的请求！')
    return redirect(url_for('auth.login'))

<<<<<<< HEAD
@auth.route('/confirm', methods=['GET', 'POST'])
=======

@auth.route('/confirm')
>>>>>>> 261682909a596851ad7bcdd749f8e98e95c7e540
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('一封新的认证邮件已经发送到您的邮箱。')
    return redirect(url_for('imanager.itemboard'))

<<<<<<< HEAD
@auth.route('/unconfirmed', methods=['GET', 'POST'])
=======

@auth.route('/unconfirmed')
>>>>>>> 261682909a596851ad7bcdd749f8e98e95c7e540
def unconfirmed():
    # 当前用户为匿名用户或当前用户已认证，直接返回主页
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('imanager.itemboard'))
    return render_template('auth/unconfirmed.html')
