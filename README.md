本程序大部分为《flask-web开发》内容：
1，数据库：heroku自带的PostgreSQL
2，模板：flask_bootstrap自带的模板
3，实现功能：
	3.1登录，注册，用户信息cookie管理：使用flask_login模块实现
		3.1.1其中用户验证方式为发送邮件
		3.1.2包括修改密码，邮箱功能
	3.2发表心情：前端<->视图函数<->数据库（数据库一对多关系）
	3.3评论心情：前端<->视图函数<->数据库（数据库一对多关系）
	3.4关注：前端<->视图函数<->数据库（数据库多对多关系）
	3.5看图：爬取煎蛋网图片url->数据库->视图函数->前端
		每次访问时都从头运行，若有新图则更新数据库，否则不更新
	3.6用户资料的添加，修改
