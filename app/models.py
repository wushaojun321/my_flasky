#encoding:utf8
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from flask import current_app,request
from datetime import datetime
import hashlib
import bleach
from markdown import markdown



class Permission():
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tag = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                        tags=allowed_tag, strip=True))
db.event.listen(Comment.body, 'set', Comment.on_change_body)


class Role(db.Model):
    #定义Role的数据库模型
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)  
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean,default=False,index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
    @staticmethod
    def insert_role():
        roles = {
            'User':(Permission.FOLLOW|
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES,True),
            'Moderate':(Permission.FOLLOW|
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES|
                    Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
            }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class Follow(db.Model):
    '''创建多对多关系，实现关注功能'''
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model,UserMixin):
    #定义User的数据库模型
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))  #这里传入的是加密后的密码
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], 
                                backref=db.backref('follower', lazy='joined'), 
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], 
                                backref=db.backref('followed',lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')


    def  __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        #继承了父类的初始化方法,super等价于UserMixin
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
            #验证email是否为设置的管理员的email
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
            #如果经过了上一步权限还为空，就给个默认的User权限
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)
    def follow(self, user):
        '关注别人'
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def gravatar(self, size=100, default='identicon', rating='g'):
        '生成头像链接'
        url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                    url=url, hash=hash, size=size, default=default, rating=rating)

    def ping(self):
        #刷新用户的最后访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def can(self,permissions):
        #这个方法用来传入一个权限来核实用户是否有这个权限,返回bool值
        return self.role is not None and\
        (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
            #这个函数需要两个参数，一个密匙，从配置文件获取，一个时间，这里1小时
        return s.dumps({'confirm':self.id})
            #为ID生成一个加密签名，然后再对数据和签名进行序列化，生成令牌版字符串（就是一长串乱七八糟的东西）
            #然后返回
    def confirm(self,token):
        #激活
        s = Serializer(current_app.config['SECRET_KEY'])
        #传入和刚才一样的密匙，解码要用
        try:
            data = s.loads(token)#解码
        except:
            return False 
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True #解的码和已经登录的账号ID相等时操作数据库改变User.confirmed的值为True
        db.session.add(self)
        db.session.commit()
        return True #激活成功返回True
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    @property
    def password(self):
        #增加密码的不可读属性，防止密码泄露
        raise AttributeError('password is not readable')

    @password.setter
    def password(self,password):
        #将传入的密码进行加密
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        #定义比较密码的方法：传入用户输入的密码，返回bool值
        return check_password_hash(self.password_hash,password)


    @staticmethod
    def generate_fake(count=100):
        #生成虚拟用户
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirm=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    @property
    def followed_posts(self):
        '这里不能用被注释的，因为它返回的是Query，我们需要的是BaseQuery，前者是后者的父类'
        # return db.session.query(Post).select_from(Follow).\
        #         filter_by(follower_id=self.id).\
        #         join(Post, Follow.followed_id==Post.author_id)
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    #登录状态管理
    return User.query.get(int(user_id))

class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()





