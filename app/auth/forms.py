#encoding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email,Regexp,EqualTo
from ..models import User
from wtforms import ValidationError

class LoginForm(Form):
	#登录表格
	email = StringField('Email', validators=[Required(), 
										Length(1,64), Email()]) #验证Email格式，长度
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('30天内自动登录')
	submit = SubmitField('登录')	


class RegistrationForm(Form):
	#注册表格
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
    	#定义方法完成与数据库交互，用来判断邮箱是否已经存在
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangePasswordForm(Form):
    #修改密码表格
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    #表单中完成密码与确认密码一致性的验证
    password2 = PasswordField('确认新密码', validators=[Required()])
    submit = SubmitField('更改密码')

class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')

class PasswordResetForm(Form):
    #重置密码
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认新密码', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('此邮箱未注册')


class ChangeEmailForm(Form):
    #修改邮箱
    email = StringField('新邮箱', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('更改邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此邮箱已注册！')

