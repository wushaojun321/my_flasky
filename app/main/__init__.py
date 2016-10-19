#encoding:utf8
from flask import Blueprint

main = Blueprint('main',__name__) #main为蓝本名称，__name__为蓝图所在的模块或者包

#切记最后再导入main文件包下的模块，以防止循环导入报错
from . import views
