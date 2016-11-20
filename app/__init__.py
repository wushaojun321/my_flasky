#encoding:utf8
from flask import Flask
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_moment import Moment

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_views = 'auth.login'

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()



def create_app():
	app = Flask(__name__)

	app.config.from_object(Config)
	Config.init_app(app)
	
	#初始化所要用到的模块
	login_manager.init_app(app)
	bootstrap.init_app(app)	
	db.init_app(app)
	mail.init_app(app)
	moment.init_app(app)

	#从/main/__init__.py中获取蓝图，并注册蓝图
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)
	return app
