from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id                 = db.Column(db.Integer(), primary_key=True)
    # username           = db.Column(db.String(64), unique=True, nullable=False)
    email              = db.Column(db.String(64), unique=True, index=True, nullable=False)
    # description        = db.Column(db.Text(), nullable=False)
    # location           = db.Column(db.String(255), nullable=False)
    password_hash      = db.Column(db.String(255), nullable=False)
    chats              = db.relationship('Chat', backref='user', lazy='dynamic')
    
    def __init__(self, email="", password=""):
        # self.username         = username
        self.email            = email
        self.password_hash    = generate_password_hash(password)
        # self.location         = location
        # self.description      = description

    def __repr__(self):
        return '<User %r>' % self.email

    @property
    def password(self):
        raise AttributeError("Password should not be read like this")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return not "" == self.email

    def is_anonymous(self):
        return "" == self.email


class Chat(db.Model):
    __tablename__ = "chats"

    id                 = db.Column(db.Integer(), primary_key=True)
    user_id            = db.Column(db.Integer(), db.ForeignKey('users.id'))
    doc_name           = db.Column(db.String(255))
    summary            = db.Column(db.Text())
    messages           = db.relationship('Message', backref='chat', lazy='dynamic')
    timestamp          = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, user_id, doc_name, summary):
        self.user_id = user_id
        self.doc_name = doc_name
        self.summary = summary

    def __repr__(self):
        return '<Chat %r>' % self.doc_name


class Message(db.Model):
    __tablename__ = "messages"

    id                 = db.Column(db.Integer(), primary_key=True)
    chat_id            = db.Column(db.Integer(), db.ForeignKey('chats.id'))
    user_id            = db.Column(db.Integer(), db.ForeignKey('users.id'))
    message            = db.Column(db.Text())
    is_user            = db.Column(db.Boolean())
    timestamp          = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, chat_id, user_id, message, is_user):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message = message
        self.is_user = is_user
    
    def __repr__(self):
        return '<Message %r>' % self.message