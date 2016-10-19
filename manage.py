#encoding:utf8

from flask_script import Manager #这里引入Manager模块，方便以后测试

from app import create_app

app = create_app()
manager = Manager(app)  #初始化Manager

if __name__ == '__main__':
#	manager.run()
	app.run(host='0.0.0.0',port=80,debug=True)
