from cgi import parse_multipart
from .database import db 
from flask_security import UserMixin
from flask_login import login_manager
from email_validator import validate_email

class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer(), autoincrement = True, primary_key = True)
    username = db.Column(db.String(70), nullable=False, unique=True)
    email = db.Column(db.String(), nullable = False, unique=True)
    password  = db.Column(db.String(255), nullable = False)
    active = db.Column(db.Boolean())
    coins = db.Column(db.Integer(),nullable=False)
    roles = db.relationship('Role', secondary = 'User_Role', backref=db.backref('User', lazy='dynamic'))
    venues = db.relationship('Venue', backref=db.backref('User', lazy=True))
    booked = db.relationship('Show', secondary= "User_Tickets", backref=db.backref("User", lazy='dynamic') )

class Role(db.Model):
    __tablename__ = 'Role'
    id = db.Column(db.Integer(), autoincrement= True, primary_key= True)
    name = db.Column('role_name', db.String(50), nullable = False, unique=True)

class UserRole(db.Model):
    __tablename__ = "User_Role"
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(),db.ForeignKey("User.id", ondelete= "CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("Role.id", ondelete="CASCADE"))

class UserTickets(db.Model):
    __tablename__ = "User_Tickets"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("User.id", ondelete="CASCADE"))
    ticket_id = db.Column(db.Integer(), db.ForeignKey("Show.show_id", ondelete="CASCADE"))
    count = db.Column(db.Integer(), nullable=False, default=0)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column('venue_id',db.Integer(), primary_key= True, autoincrement=True)
    name = db.Column(db.String(), nullable=False )
    place = db.Column(db.String(), nullable=False)
    capacity = db.Column(db.String(), nullable=False)
    created_by = db.Column('owner',db.Integer(), db.ForeignKey('User.id'))
    shows = db.relationship('Show', backref=db.backref('Venue', lazy=True))
    

class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column('show_id',db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer())
    ticket_price = db.Column(db.Integer(),nullable=False)
    start = db.Column(db.DateTime(), nullable=False)
    end = db.Column(db.DateTime(), nullable=False)
    tags= db.Column(db.JSON(), nullable=True)
    ticket_count = db.Column(db.Integer(), nullable=False)
    photo = db.Column('photo', db.LargeBinary)
    at_venue = db.Column('venue',db.Integer(), db.ForeignKey('Venue.venue_id', ondelete="CASCADE"))

def init_db():
    print("Database created")
    db.create_all()
    # admin_role = Role("Admin")
    # user_role = Role("User")
    # db.session.add(admin_role)
    # db.session.add(user_role)
    # db.session.commit()

if __name__ == "main":
    print('Running')
    init_db()