#encoding:utf8

import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
	MAIL_SERVER ='smtp.qq.com'
	MAIL_PORT =587
	MAIL_USE_TLS =True
	MAIL_USERNAME ='418836702'
	MAIL_PASSWORD ='vvbaojrkvldubhdg'
	SECRET_KEY = 'python123'
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASK_ADMIN = '418836702@qq.com'
	@staticmethod
	def init_app(app):
		pass
