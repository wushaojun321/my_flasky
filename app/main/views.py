#encoding:utf8

from flask import render_template
from . import main #导入蓝图

@main.route('/')
def index():
	return render_template('index.html') 
