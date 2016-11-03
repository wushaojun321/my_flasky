#encoding:utf8

import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
	@staticmethod
	def init_app(app):
		pass
