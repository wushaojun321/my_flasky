#encoding:utf8

from . import mail
from flask_mail import Message
from flask import render_template, current_app

def send_email(to, subject, template, **kwargs):
	app = current_app._get_current_object()#这里不太懂，牵扯到异步，反正是配置验证信息的
	msg = Message(subject,sender='418836702@qq.com',recipients=[to])#实例化一个Message对象，准备发送邮件，接受者为to
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)#将准备好的模板添加到msg对象上，字典传的参里包括token(即生成的一长串字符串)，链接的组装，页面的渲染在里面用jinja2语法完成
	with app.app_context():
		mail.send(msg) #发射
