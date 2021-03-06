#encoding:utf8

import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
	MAIL_SERVER ='smtp.qq.com'
	MAIL_PORT =587
	MAIL_USE_TLS =True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SECRET_KEY = 'python123'
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
	@staticmethod
	def init_app(app):
		pass
