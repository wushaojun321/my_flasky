#encoding:utf8

from flask_script import Manager,Shell #这里引入Manager模块，方便以后测试
from app.models import User,Role,Post,Follow
from app import db
from app import create_app
from flask_migrate import Migrate, MigrateCommand

app = create_app()
manager = Manager(app)  #初始化Manager
migrate = Migrate(app, db)

def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role, Post=Post, Follow=Follow)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()
	# app.run(host='0.0.0.0',port=80,debug=True)
