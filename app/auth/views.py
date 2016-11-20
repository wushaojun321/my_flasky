#encoding:utf8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from ..models import User,Permission
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,\
                    PasswordResetRequestForm,PasswordResetForm,ChangeEmailForm
from .. import db
from ..email import send_email
from ..decorators import admin_required,permission_required

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/admin')
@admin_required
def admin():
    return '你好，老公1-_-'

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')
    # return 'hehe'

@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password')			
	return render_template('/auth/login.html',form = form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('已经登出！')
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
	#注册
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()  #这里不能等数据库自动保存，因为用户在验证时需要登录
        token = user.generate_confirmation_token()  #生成HASH码
        send_email(user.email, 'Confirm Your Account',
					'auth/email/confirm', user=user, token=token)#发送验证信息
        flash('邮件已经发送,请先登录再验证！')
        return redirect(url_for('auth.login'))#重定向到登录页面
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		#如果你已经激活过了
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		#去激活并且激活成功了
		flash('O了！')
	else:
		flash('你是盗号的还是迟到鬼?')
	return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required  #只有登录的人才能修改密码
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            #这里引入user的上下文，这个概念不太懂，暂且当成全局变量来用
            current_user.password = form.password.data
            #修改密码
            db.session.add(current_user)
            #加入数据库的session，这里不需要.commit()，在配置文件中已经配置了自动保存
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        #验证密码是否为登录状态，如果是，则终止重置密码
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            #如果用户存在
            token = user.generate_reset_token()
            #调用User模块中的generate_reset_token函数生成验证信息
            send_email(user.email,'重置密码','auth/email/reset_password',
                        user=user,token=token,next=request.args.get('next'))
            #调用send_email函数，渲染邮件内容之后发送重置密码邮件
        flash('重置密码的邮件已经发送，请查收！')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))