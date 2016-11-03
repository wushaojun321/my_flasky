#encoding:utf8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app():
	app = Flask(__name__)

	app.config.from_object(Config)
	Config.init_app(app)
	
	#初始化所要用到的模块
	bootstrap.init_app(app)	
	db.init_app(app)

	#从/main/__init__.py中获取蓝图，并注册蓝图
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	return app
