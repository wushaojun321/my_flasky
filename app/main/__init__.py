#encoding:utf8
from flask import Blueprint

main = Blueprint('main',__name__) #main为蓝本名称，__name__为蓝图所在的模块或者包

#切记最后再导入main文件包下的模块，以防止循环导入报错
from . import views
from ..models import Permission

@main.app_context_processor
#这里牵扯到上下文处理器
def inject_permissions():
	#将auth中的Permission类导入到main中，因为权限验证不仅在auth中用到
    return dict(Permission=Permission)