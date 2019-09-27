# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 @Time    : 2019/9/17 15:07
 @Author  : Jay Chen
 @FileName: models.py
 @GitHub  : https://github.com/cRiii
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from jaysblog.extensions import db
from flask_login import UserMixin


class BaseModel(object):
    # 模型基类 为所有模型添加创建和更新的时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel, db.Model, UserMixin):
    """
        UserMixin表示通过认证的用户
            is_authenticated 表示用户已通过认证 返回True 否则False
            is_active 表示允许用户登陆 返回True 否则False
            is_anonymous 表示如果当前未用户登陆(匿名用户) 返回True 否则False
            get_id() 以unicode形式返回用户唯一标识
    """
    __tablename__ = 'b_users'

    id = db.Column(db.Integer, primary_key=True)  # 用户id
    nick_name = db.Column(db.String(32), unique=True, nullable=False)  # 用户名
    password_hash = db.Column(db.String(128), nullable=False)  # 用户密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号码
    email = db.Column(db.String(64), unique=True, nullable=True)  # 邮箱
    desc = db.Column(db.Text)  # 个人简介
    avatar_url = db.Column(db.String(256))  # 用户头像路径
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    last_login_time = db.Column(db.DateTime, default=datetime.now)  # 最后一次登陆时间
    is_delete = db.Column(db.Integer, default=1)  # 用户是否被删除 1正常  0被删除
    gender = db.Column(
        db.Enum(
            'MAN',  # 男
            'WOMAN'  # 女
        ), default='MAN'
    )

    @property
    def password(self):
        raise AttributeError(u'该属性不可读')

    @password.setter
    def password(self, value):
        """
            generate_password_hash（password，method='pbkdf2：sha256'，salt_length=8）
                method指定计算散列值的方法
                salt_length 指定盐长度
        """
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        """
            接收散列值 和 密码作比较 返回布尔类型
            check_password_hash（pwhash，password）
        """
        return check_password_hash(self.password_hash, password)


class Post(BaseModel, db.Model):
    __tablename__ = 'b_posts'

    id = db.Column(db.Integer, primary_key=True)  # 文章编号
    post_title = db.Column(db.String(256), nullable=False)  # 文章标题
    post_user_id = db.Column(db.Integer, nullable=False)  # 创建文章用户
    post_digest = db.Column(db.String(512), nullable=True)  # 文章简介
    post_content = db.Column(db.Text, nullable=False)  # 文章内容
    post_clicks = db.Column(db.Integer, default=0)  # 点击量
    post_like_num = db.Column(db.Integer, default=0)  # 点赞数量
    post_index_image_url = db.Column(db.String(256))  # 主页面列表图片地址
    post_status = db.Column(db.Integer, default=1)  # 文章状态
    post_can_comment = db.Column(db.Integer, default=1)  # 当前文章是否可以被评论

    post_comments = db.relationship('Comment', backref='comment_post')  # 当前文章的评论
    post_category = db.relationship('Category', back_populates='cg_posts')
    post_category_id = db.Column(db.Integer, db.ForeignKey('b_category.id'), nullable=False)  # 文章类型

    def to_dict(self):
        res_dict = {
            "id": self.id,
            "post_title": self.post_title,
            "post_user_id": self.post_user_id,
            "post_digest": self.post_digest if self.post_digest else "",
            "post_clicks": self.post_clicks,
            "post_like_num": self.post_like_num,
            "post_index_image_url": self.post_index_image_url if self.post_index_image_url else "",
            "post_category": self.post_category.to_dict() if self.post_category else None,
            "post_comments_count": len(self.post_comments) if self.post_comments else 0,
        }
        return res_dict

    def to_dict_details(self):
        res_dict = {
            "id": self.id,
            "post_title": self.post_title,
            "post_user_id": self.post_user_id,
            "post_content": self.post_content,
            "post_clicks": self.post_clicks,
            "post_like_num": self.post_like_num,
            "post_can_comment": self.post_can_comment,
            "post_category": self.post_category.to_dict() if self.post_category else None,
        }
        return res_dict


class Category(BaseModel, db.Model):
    __tablename__ = 'b_category'

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    cg_name = db.Column(db.String(64), nullable=False, unique=True)  # 分类名称

    cg_posts = db.relationship('Post', back_populates='post_category')  # 分类下的文章

    def to_dict(self):
        res_dict = {
            "id": self.id,
            "cg_name": self.cg_name,
            "cg_posts_count": len(self.cg_posts) if self.cg_posts else 0
        }
        return res_dict


class Comment(BaseModel, db.Model):
    __tablename__ = 'b_comments'

    id = db.Column(db.Integer, primary_key=True)  # 评论编号
    comment_user_id = db.Column(db.Integer, nullable=False)  # 评论用户ID
    comment_content = db.Column(db.Text, nullable=False)  # 评论内容
    comment_from_admin = db.Column(db.Integer, default=0)  # 是否为管理员评论
    comment_status = db.Column(db.Integer, default=0)  # 评论是否通过审核  -1不可用 0:审核中 1:审核通过

    comment_post_id = db.Column(db.Integer, db.ForeignKey('b_posts.id'), nullable=False)  # 当前评论属于的文章id
    comment_reply = db.relationship('Reply', backref='reply_comment')  # 当前评论下的回复

    def to_dict(self):
        comment_replies = []
        if self.comment_reply is not []:
            for reply in self.comment_reply:
                if reply.reply_status == 1:
                    comment_replies.append(reply.to_dict())

        res_dict = {
            "id": self.id,
            "comment_user_name": User.query.filter_by(id=self.comment_user_id).first().nick_name,
            "comment_content": self.comment_content,
            "comment_from_admin": self.comment_from_admin,
            "comment_post_id": self.comment_post_id,
            "comment_replies": comment_replies
        }
        return res_dict


class Reply(BaseModel, db.Model):
    __tablename__ = 'b_reply'

    id = db.Column(db.Integer, primary_key=True)  # 回复的id
    reply_from_user = db.Column(db.String(32), nullable=False)  # 谁回复的
    reply_to_user = db.Column(db.String(32), nullable=False)  # 回复给谁的
    reply_content = db.Column(db.Text, nullable=False)  # 回复的内容
    reply_status = db.Column(db.Integer, default=0)  # 回复是否通过审核  -1不可用 0:审核中 1:审核通过

    reply_comment_id = db.Column(db.Integer, db.ForeignKey('b_comments.id'), nullable=False)  # 当前回复属于的评论id

    def to_dict(self):
        res_dict = {
            "id": self.id,
            "reply_from_user": self.reply_from_user,
            "reply_to_user": self.reply_to_user,
            "reply_content": self.reply_content,
            "reply_comment_id": self.reply_comment_id
        }
        return res_dict




