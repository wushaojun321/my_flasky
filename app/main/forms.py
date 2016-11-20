#encoding:utf8

from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User


class EditProfileForm(Form):
	name = StringField('真名',validators=[Length(0,64)])
	location = StringField('来自',validators=[Length(0,64)])
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')

class EditProfileAdminForm(Form):
	#管理员的修改用户资料表单
    email = StringField('电子邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('是否激活')
    role = SelectField('权限', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
    	#确保数据发生变化并且不与数据库中数据冲突
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class PostForm(Form):
    body = TextAreaField('大兄弟，今天心情如何？', validators=[Required()])
    submit = SubmitField('提交')

class CommentForm(Form):
    body = StringField('',validators=[Required()])
    submit = SubmitField('提交')