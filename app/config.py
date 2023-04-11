import os
b_dir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig():
    SQLITE_DB_DIR = os.path.join(b_dir, "../database_dir")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "ticket_show1.sqlite3")
    DEBUG = False
    SECRET_KEY = "Ayushi Ayushi Ayushi Ayushi"
    SECURITY_PASSWORD_HASH = "bcrpyt"
    SECUROITY_REGSITRABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None   