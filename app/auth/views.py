#encoding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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
    #管理员权限验证页面
    return '你好，老公1-_-'

@auth.route('/unconfirmed')
def unconfirmed():
    #未验证用户登录后页面
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')
    # return 'hehe'

@auth.route('/login',methods=['GET','POST'])
def login():
    #登录路由
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('邮箱或密码错误！')			
	return render_template('/auth/login.html',form = form)

@auth.route('/logout')
@login_required
def logout():
    #登出路由
	logout_user()
	flash('已经登出！')
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
	#注册路由
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
    #激活路由
	if current_user.confirmed:
		#如果你已经激活过了
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		#去激活并且激活成功了
		flash('激活成功！')
	else:
		flash('你是盗号的还是迟到鬼?')
	return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('验证邮件已发送，请查收！')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required  #只有登录的人才能修改密码
def change_password():
    #修改密码
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            #这里引入user的上下文，这个概念不太懂，暂且当成全局变量来用
            current_user.password = form.password.data
            #修改密码
            db.session.add(current_user)
            #加入数据库的session，这里不需要.commit()，在配置文件中已经配置了自动保存
            db.session.commit()
            flash('您的密码修改成功！')
            return redirect(url_for('main.index'))
        else:
            flash('密码不正确！')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    #重置密码请求路由
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
    #重置密码处理路由
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的密码已经重置！')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    #修改email请求路由
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('验证信息已经发送，晴查收！')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱或密码错误！')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    #修改邮箱处理路由
    if current_user.change_email(token):
        flash('您的邮箱已经修改！')
    else:
        flash('邮箱修改失败！')
    return redirect(url_for('main.index'))