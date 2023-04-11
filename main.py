from urllib import request
from flask import Flask
import sqlalchemy
import os
import flask_sqlalchemy 
from app.config import LocalDevelopmentConfig
from app.models import User, Role, UserRole
from app.database import db
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from flask_login import LoginManager
from flask_migrate import Migrate
from flask import render_template, redirect, request
# from app.database import db

app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == 'production':
        # app.logger.info("Currently no production config is setup.")
        raise Exception("Currently no production config is setup.")
    elif os.getenv('ENV', "development") == "testing":
        app.logger.info("Starting Testing.")
        print("Starting Testing")
        # app.config.from_object(TestingConfig)
    else:
        print("Starting Local Development.")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    
    @app.before_first_request
    def create_tables():
        db.create_all()
        roles = Role.query.all()
        if len(roles) < 2:
            admin = Role(name="admin")
            user = Role(name="user")
            db.session.add(admin)
            db.session.add(user)
            db.session.commit()
        if current_user.is_authenticated:
            app.config['identity'] = current_user.roles
    app.app_context().push()
    

    from app.controllers import auth as auth_blueprint 
    app.register_blueprint(auth_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.admin_login'
    login_manager.login_view = 'auth.user_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    migrate = Migrate(app, db)
    app.app_context().push()
    # user_datastore = SQLAlchemySessionUserDatastore(db.session, User)
    # security = Security(app, user_datastore)

    return app

app = create_app()

from app.controllers import *

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=8080) 