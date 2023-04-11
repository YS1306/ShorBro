from flask import Flask, redirect, request, render_template, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from .models import User, Role, UserRole, Venue, Show, UserTickets
from .database import db
from flask_security import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from flask_login import login_user, current_user
from flask import session
import json
from datetime import datetime
from flask_migrate import Migrate
from PIL import Image, ImageOps 
from io import BytesIO
import base64
from flask import jsonify
app.jinja_env.filters['strftime'] = datetime.strftime


auth = Blueprint("auth", __name__)


@app.route("/", methods=["GET", "POST"])
# @app.route("/<user>",defaults={'user': ''}, methods=["GET", "POST"])
def home():
    ad_ex = Role.query.filter_by(name="admin").first()
    us_ex = Role.query.filter_by(name="user").first()
    if not ad_ex and not us_ex:
        admin_role = Role(name="admin")
        user_role = Role(name="user")
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()
    venues = Venue.query.all()
    shows = Show.query.all()
    
    curr_time = datetime.now()
    # curr_time = curr_time.strftime("%Y-%m-%dT%H:%M")
    # show_start = datetime.strptime(show_start)
    for show in shows:
        if show.end < curr_time:
            shows.remove(show)
            db.session.delete(show)
    db.session.commit()
    shows = Show.query.order_by(Show.start.asc()).all()
    venue_shows = dict()
    for show in shows:
        venue_shows[show] = []
        for venue in venues:
            if venue.id == show.at_venue:
                venue_shows[show].append(venue.name)
                venue_shows[show].append(venue.place)

        encoded_image = base64.b64encode(show.photo).decode('utf-8')
        venue_shows[show].append(encoded_image)

    
    return render_template("home.html", shows=shows, venues=venues, venue_shows=venue_shows)

@app.route("/About", methods=["GET"])
def about_page():
    return render_template("about_page.html")

@auth.route('/admin_signup', methods=['GET'])
def admin_signup():
    return render_template('admin_sign_log.html')


@auth.route('/admin_signup', methods=['POST'])
def admin_signup_post():
    # user_id = request.form.get('userid')
    user_name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    coins = 1000
    role = Role.query.filter_by(id=1).first()
    admin = User.query.filter(User.roles.contains(role)).first()
    if admin:
        flash(" Admin already exists, Cannot add another admin!!. Instead register as a User.")
        return redirect(url_for('auth.admin_signup'))
    if email == '' or user_name == '' or password == '':
        flash('Insuficient Details. Please provide all the required fiels!')
        return redirect(url_for('auth.admin_signup'))
    with db.session.no_autoflush:
        user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exits.Try with a new one!')
        return redirect(url_for('auth.admin_signup'))
    
    new_user = User(username=user_name, email=email, password=generate_password_hash(
        password, method='sha256'), active=1, coins=coins)
    new_user.roles.append(role)
    
    db.session.add(new_user)
    new_user = User.query.filter_by(username=user_name).first()
    
    db.session.commit()
    login_user(new_user, remember=remember)
    session['username'] = new_user.username
    return redirect(url_for('home'))
    


@auth.route('/user_signup', methods=['GET'])
def user_signup():
    return render_template('user_sign_log.html')


@auth.route('/user_signup', methods=['POST'])
def user_signup_post():
    # user_id = request.form.get('userid')
    user_name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if email == '' or user_name == '' or password == "":
        flash('Insufficent Details for User Registration !')
        return redirect(url_for('auth.user_signup'))
    if user:
        flash('Email address already exits.Try with a new one!')
        return redirect(url_for('auth.user_signup'))
    role = Role.query.filter_by(id=2).first()
    new_user = User(username=user_name, email=email, password=generate_password_hash(
        password, method='sha256'), active=1,coins=1000)
    new_user.roles.append(role)
    # new_user.roles.append(role)
    db.session.add(new_user)
    new_user = User.query.filter_by(email=email).first()
    # user_role = UserRole(user_id=new_user.id, role_id=2)
    # db.session.add(user_role)
    db.session.commit()
    login_user(new_user, remember=remember)
    session['username'] = new_user.username
    return redirect(url_for('home'))
    # return redirect(url_for('__auth__.login'))


@auth.route('/admin_login')
def admin_login():
    return render_template('admin_sign_log.html')


@auth.route('/admin_login', methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    if email != "":
        user = User.query.filter_by(email=email).first()
    elif username != '':
        user = User.query.filter_by(username=username).first()
    else:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.admin_login'))
    if not user:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.admin_login'))
    elif not check_password_hash(user.password, password):
        flash("Incorrect Password. Enter the correct password!!")
        return redirect(url_for('auth.admin_login'))
    user_role = UserRole.query.filter_by(user_id=user.id).first()
    
    if user_role.role_id == 1:
        user.active = 1
        db.session.commit()
        login_user(user, remember=remember)
        session['username'] = user.username
        
        return redirect(url_for('home'))
    else:
        flash("Entered details do not belong to an admin. Try again with correct credentials.")
        return redirect(url_for('auth.admin_login'))


@auth.route('/user_login')
def user_login():
    return render_template('user_sign_log.html')


@auth.route('/user_login', methods=['POST'])
def user_login_post():
    email = request.form.get('email')
    user_name = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    if email != '':
        user = User.query.filter_by(email=email).first()
    elif user_name != '':
        user = User.query.filter_by(username=user_name).first()
    else:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.admin_login'))    
    if not user:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.user_login'))
    elif not check_password_hash(user.password, password):
        flash("Incorrect Password. Enter the correct password!!")
        return redirect(url_for('auth.user_login'))
    
    user_role = UserRole.query.filter_by(user_id=user.id).first()
    if user_role.role_id != 2:
        flash("Entered details do not belong to a User. Try again with correct credentials")
        return redirect(url_for('auth.user_login'))
    user.active = 1
    db.session.commit()
    login_user(user, remember=remember)
    session['username'] = user.username
    return redirect(url_for('home'))



@auth.route('/logout')
@login_required
def logout():
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    user.active = 0
    db.session.commit()
    logout_user()

    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dash():
    if str(current_user.roles[0]) == "<Role 1>":   
        admin = session['_user_id']
        venues= Venue.query.filter_by(created_by=admin).all()
        shows = dict()
        for venue in venues:
            shows[venue] = Show.query.filter_by(at_venue = venue.id).all()

        return render_template('admin_dash.html', venues=venues, shows=shows)
    else:
        flash("You do not have access this page.")
        return redirect(url_for('user_dash'))

@app.route('/admin/add_venue', methods=['GET', 'POST'])
@login_required
def add_venue():
    try:
        if str(current_user.roles[0]) == "<Role 1>":    
            if request.method == "GET":
                return render_template('add_venue.html')
            elif request.method == "POST":
                venue_name = request.form.get('venue_name')
                place = request.form.get('place')
                capacity = request.form.get('capacity')
                owner = session['_user_id']
                

                venue = Venue(name=venue_name, place=place, capacity=capacity, created_by=owner)
                user = User.query.filter_by(id=owner).first()
                user.venues.append(venue)
                db.session.add(venue)
                db.session.add(user)
                db.session.commit()

                return redirect(url_for('admin_dash'))
        else:
            flash("You do not have access to the page you are trying to request.")
            return redirect(url_for('user_dash'))
    except:
        flash("Invalid venue access")
        return redirect(url_for('home'))

@app.route("/admin/delete_venue", methods=["GET","POST"])
@login_required
def delete_venue():
    try:
        if str(current_user.roles[0]) == "<Role 1>":        
            venue_id = request.args.get('venue')
            venue = Venue.query.filter_by(id=venue_id).first()
            shows = Show.query.filter_by(at_venue=venue_id).all()
            for show in shows:
                db.session.delete(show)
            db.session.delete(venue)
            db.session.commit()
            return redirect(url_for("admin_dash"))
        else:
            pass
    except:
        flash("Show already deleted")
        return redirect(url_for('home'))

@app.route("/admin/edit_venue", methods=["GET", "POST"])
@login_required
def edit_venue():
    try:
        if str(current_user.roles[0]) == "<Role 1>":    
            if request.method == 'GET':
                venue_id = request.args.get('venue')
                venue = Venue.query.filter_by(id=venue_id).first()
                return render_template("edit_venue.html", venue=venue)
            elif request.method == "POST":
                venue_id = request.args.get('venue')
                new_name = request.form.get('new_name')
                new_place = request.form.get('new_place')
                new_capacity = request.form.get('new_capacity')
                venue = Venue.query.filter_by(id=venue_id).first()
                venue.name = new_name 
                venue.place = new_place
                venue.capacity = new_capacity
                db.session.add(venue)
                db.session.commit()
                return redirect(url_for("admin_dash"))
        else:
            flash("Access denied")
            return redirect(url_for('home'))
    except:
        flash("Venue Does not exist")
        return redirect(url_for('home'))
    

@app.route("/admin/add_show", methods=["GET" , "POST"])
@login_required
def add_show():
    try:
        if str(current_user.roles[0]) == "<Role 1>":    
            if request.method == "GET": 
                venue_id = request.args.get('venue')
                return render_template("add_show.html", venue=venue_id)
            elif request.method == "POST":
                # flask db migrate -m "Add start column to Show table"
                # flask db upgrade
                venue_id = request.args.get('venue')
                show_name = request.form.get('show_name')
                show_ticket = request.form.get('show_ticket')
                show_rating = request.form.get('show_rating')
                show_tags = request.form.get('show_tags')
                show_start = request.form.get('show_start')
                show_end = request.form.get('show_end')
                image = request.files['photo']

                venue = Venue.query.filter_by(id=venue_id).first()
                ticket_count = venue.capacity
                show_start = datetime.strptime(show_start, "%Y-%m-%dT%H:%M")
                show_end = datetime.strptime(show_end, "%Y-%m-%dT%H:%M")

                pre_show = Show.query.filter_by(name=show_name).first()
                
                if pre_show:
                    flash("Show already created.")
                    return render_template('add_show.html', venue=venue_id)
                
                shows = Show.query.filter_by(at_venue=venue_id).all()

                for show in shows:
                    if show.start <= show_start <= show.end or show.start <= show_end <= show.end:
                        flash("Oopss! Another show booked in the current timing at this venue.")
                        return render_template("add_show.html", venue=venue_id)
                show_tags = show_tags.rstrip()
                show_tags = json.dumps( show_tags.split(' '))
                
                image_data = image.read()
                image_data =BytesIO(image_data)
                img = Image.open(image_data)

                desired_ratio = 3/2
                current_ratio = img.width / img.height
                
                if current_ratio != desired_ratio: 
                        new_width = 300
                        new_height = int(desired_ratio*new_width)
                        img = img.resize((new_width, new_height))
                        img = ImageOps.expand(img)


                with BytesIO() as output:
                    img.save(output, format="jpeg")
                    image_data = output.getvalue()

                show = Show(name=show_name, rating=show_rating, ticket_price=show_ticket,start=show_start, 
                            end=show_end,tags=show_tags,ticket_count=ticket_count, at_venue=venue_id, photo=image_data)
                
                venue.shows.append(show)
                db.session.add(show)
                db.session.add(venue)
                db.session.commit()
                
                return redirect(url_for("admin_dash", shows=shows))
        else:
            flash("Access denied")
            return redirect(url_for('home'))    
    except:
        flash("Invalid Access")
        return redirect(url_for("home"))
    


@app.route("/admin/edit_show", methods=["GET", "POST"])
@login_required
def show_actions():
    try:
        if str(current_user.roles[0]) == "<Role 1>":    
            if request.method == 'GET':
                show_id = request.args.get('show')
                show = Show.query.filter_by(id=show_id).first()
                temp = json.loads(show.tags)
                
                tags = ''
                for tag in temp:
                    tags += tag +' '

                return render_template("edit_show.html", show=show , tags=tags)
                
            
            if request.method == "POST":
                show_id = request.args.get('show')
            
                show_name = request.form.get('show_name')
                show_ticket = request.form.get('show_ticket')
                show_rating = request.form.get('show_rating')
                show_tags = request.form.get('show_tags')
                show_start = request.form.get('show_start')
                show_end = request.form.get('show_end')
                image = request.files['photo']

                show_start = datetime.strptime(show_start, "%Y-%m-%dT%H:%M")
                show_end = datetime.strptime(show_end, "%Y-%m-%dT%H:%M")
                
                show = Show.query.filter_by(id=show_id).first()
            
                pre_show = Show.query.filter_by(name=show_name).first()
                
                if pre_show and pre_show.id != int(show_id):
                    flash("A show of this name already exists. Cannot set the show name to this.")
                    return redirect(url_for("show_actions", show=show_id))
                
                show_tags = json.dumps(show_tags.split(" "))

                show.name = show_name   
                show.rating = show_rating
                show.ticket_price = show_ticket
                show.tags = show_tags
                show.start = show_start
                show.end = show_end
                if image:
                    image_data = image.read()
                    image_data =BytesIO(image_data)
                    img = Image.open(image_data)
                    desired_ratio = 3/2
                    current_ratio = img.width / img.height
                    
                    if current_ratio != desired_ratio: 
                        new_width = 300
                        new_height = int(desired_ratio*new_width)
                        img = img.resize((new_width, new_height))
                        img = ImageOps.expand(img)


                    with BytesIO() as output:
                        img.save(output, format="jpeg")
                        image_data = output.getvalue()
                    show.photo = image_data

                # show = Show(name=show_name, rating=show_rating, ticket_price=show_ticket,start=show_start, 
                #             end=show_end,tags=show_tags,ticket_count=ticket_count, at_venue=venue_id, photo=image_data, photo)


                db.session.add(show)
                db.session.commit()
                return redirect(url_for("admin_dash"))
        else:
            flash("Access denied")
            return redirect(url_for('home'))
    except:
        flash("Show has ended.")  
        return redirect(url_for('home'))

@app.route("/admin/delete_show", methods=['GET', "POST"])
@login_required
def delete_show():
    try:
        if str(app.config['identity'][0]) == "<Role 1>":    
            if request.method == "POST":
                show = request.args.get('show')
                show = Show.query.filter_by(id=show).first()
                db.session.delete(show)
                db.session.commit()
                return redirect(url_for("admin_dash"))  
        else:
            flash("Access denied")
            return redirect(url_for('home')) 
    except:
        flash("Show has ended")
        return redirect(url_for('home')) 
        

@app.route("/user/dashboard", methods=["GET"]) 
@login_required 
def user_dash():
    if request.method == "GET":
        user_id = session["_user_id"]
        user = User.query.filter_by(id=user_id).first()
        venues = Venue.query.all()
        user_tickets = UserTickets.query.filter_by(user_id=user_id).all()
        shows = user.booked
        venue_shows = {}
        # shows = []    
        # for show in booked:
        #     shows.append(Show.query.filter_by(id=show)).first()
        for show in shows:
            venue_shows[show] = []
            for venue in venues:
                if venue.id == show.at_venue:
                    venue_shows[show].append(venue.name)
                    venue_shows[show].append(venue.place)

            encoded_image = base64.b64encode(show.photo).decode('utf-8')
            venue_shows[show].append(encoded_image)
            for user_ticket in user_tickets:
                if user_ticket.ticket_id == show.id:
                    venue_shows[show].append(user_ticket.count)
        return render_template("user_dash.html", shows=shows, venue_shows=venue_shows)

@app.route("/user/view_show", methods=['GET'])
@login_required
def view_show():
    try:
        id = request.args.get('show')
        show = Show.query.filter_by(id=id).first()
        show_img = base64.b64encode(show.photo).decode('utf-8')
        temp = json.loads(show.tags)
        tags = ''
        for tag in temp:
            tags += tag + ' '
        show.tags = tags
        # show.tags = show_tags

        return render_template("view_show.html", show=show, show_img=show_img, tags=tags)
    except:
        flash("Show has ended")
        return redirect(url_for('home')) 

@app.route('/user/book_tickets', methods=["GET", "POST"])
@login_required
def book_tickets():
    try:    
        if request.method == "GET":    
            id = request.args.get("show")
            show = Show.query.filter_by(id=id).first()
            
            return render_template("book_tickets.html", show=show)
        elif request.method == "POST":
            id = request.args.get("show")
            quantity = request.form.get("quantity")
            user_id = session['_user_id']

            show = Show.query.filter_by(id=id).first()
            if int(quantity) <= show.ticket_count:
                user = User.query.filter_by(id=user_id).first()
                show.ticket_count -= int(quantity)
                if show not in user.booked:
                    user.booked.append(show)
                user_tickets = UserTickets.query.filter_by(user_id=user.id).first()
                user_tickets.count += int(quantity)
                db.session.commit()
                flash("Woohoooo! Congratulations on your booking. You can view your tickets under your dashboard.")
                return redirect(url_for("home"))
            else:
                flash("Sorry, Requested no. of tickets not available!!")
                return redirect(url_for("view_show", show=show.id))
    except:
        flash("Show has ended")
        return redirect(url_for('home')) 

@app.route('/user/search_shows', methods=["GET","POST"])
def search_shows():
    if request.method == "POST":
        key = request.form.get('key')
        
        shows = Show.query.all()
        venues = Venue.query.all()
        searched_shows = []
        venue_shows = dict()
        
        for show in shows:
            temp = json.loads(show.tags)
            tags = ''
            for tag in temp:
                tags += tag + ' '
            
            if key in tags or key in show.name:
                venue_shows[show] = []
                for venue in venues:
                    if venue.id == show.at_venue:
                        venue_shows[show].append(venue.name)    
                        venue_shows[show].append(venue.place)

                encoded_image = base64.b64encode(show.photo).decode('utf-8')
                venue_shows[show].append(encoded_image)
                searched_shows.append(show)
        return render_template("searched_shows.html",shows=searched_shows, venue_shows=venue_shows)
    

@app.route('/api/venues', methods=['GET',"POST"])
def venues_list_api():
    if request.method == "GET":
        venues = Venue.query.all()
        all_venues = []
        for venue in venues:
            venue_data = {}
            venue_data['id'] = venue.id
            venue_data['name'] = venue.name
            venue_data['place'] = venue.place
            venue_data['capacity'] = venue.capacity
            # venue_data['creator'] = venue.created_by
            # venue_data['shows'] = venue.shows
            all_venues.append(venue_data)
        return jsonify({'venues': all_venues})
    elif request.method == "POST":
        name = request.json['name']
        place = request.json['place']
        capacity = request.json['capacity']
        # admin = User.query.filter_by()
        new_venue = Venue(name=name, place=place, capacity=capacity)
        db.session.add(new_venue)
        db.session.commit()
        return jsonify({'message': 'Venue added successfully!'})

@app.route('/api/venues/<int:id>', methods=['GET'])
def get_venue_api(id):
    venue = Venue.query.filter_by(id=id).first()
    if not venue:
        return jsonify({'message': ' Requested Venue not found!'})
    venue_data = {}
    venue_data['id'] = venue.id
    venue_data['name'] = venue.name
    venue_data['place'] = venue.place
    venue_data['capacity'] = venue.capacity
    return jsonify({'venue': venue_data})

@app.route('/api/venues/<int:id>', methods=['PUT'])
def update_venue_api(id):
    venue = Venue.query.filter_by(id=id).first()
    if not venue:
        return jsonify({'message': 'The Venue you want to update does not exist.'})
    name = request.json['name']
    place = request.json['place']
    capacity = request.json['capacity']
    venue.name = name
    venue.place = place
    venue.capacity = capacity
    db.session.commit()
    return jsonify({'message': 'Venue updated successfully!'})

@app.route('/api/venues/<int:id>', methods=["DELETE"])
def delete_venue_api(id):
    venue = Venue.query.filter_by(id=id).first()
    if not venue:
        return jsonify({'message': 'The Venue you want to delete does not exist.'})
    db.session.delete(venue)
    db.session.commit()
    return jsonify({'message':"Venue deleted successfully"})

@app.route('/api/shows', methods=["GET", "POST"])
def read_shows_api():
    if request.method == "GET":
        shows = Show.query.all()
        all_shows = []
        for show in shows:
            show_data = {}
            show_data['id'] = show.id
            show_data['name'] = show.name
            show_data['rating'] = show.rating
            show_data['ticket_price'] = show.ticket_price
            show_data['start'] = show.start
            show_data['end'] = show.end
            show_data['tags'] = show.tags
            show_data['ticket_count'] = show.ticket_count
            # venue_data['creator'] = venue.created_by
            # venue_data['shows'] = venue.shows
            all_shows.append(show_data)
        return jsonify({'Shows': all_shows})
        
    elif request.method == "POST":
        name = request.json['name']
        rating = request.json['rating']
        ticket_price = request.json['ticket_price']
        start = request.json['start_time']
        end = request.json['end_time']
        tags = request.json['tags']
        ticket_count = request.json['ticket_count']
        show = Show(name=name, rating=rating, ticket_price=ticket_price, start=start, end=end, tags=tags, ticket_count=ticket_count)
        db.session.add(show)
        db.session.commit()
        return jsonify({'message':"Show Created successfully"})
    
@app.route('/api/shows/<int:id>', methods=["GET","PUT","DELETE"])
def show_crud_api(id):
    if request.method == "GET":
        show = Show.query.filter_by(id=id).first()
        if not show:
            return jsonify({'message':'No such show exists.'})
        show_data = {}
        show_data['id'] = show.id
        show_data['name'] = show.name
        show_data['rating'] = show.rating
        show_data['ticket_price'] = show.ticket_price
        show_data['start'] = show.start
        show_data['end'] = show.end
        show_data['tags'] = show.tags
        show_data['ticket_count'] = show.ticket_count
        return jsonify({'show':show_data})
    elif request.method == "PUT":
        show = Show.query.filter_by(id=id).first()
        if not show:
            return jsonify({'message':'No such show exists.'})
        name = request.json['name']
        rating = request.json['rating']
        ticket_price = request.json['ticket_price']
        start = request.json['start_time']
        end = request.json['end_time']
        tags = request.json['tags']
        ticket_count = request.json['ticket_count']
        show.name = name
        show.rating = rating
        show.ticket_price = rating
        show.start = start
        show.end = end
        show.tags = tags
        show.ticket_count = ticket_count
        db.session.commit()
        return jsonify({'message':'Show updated successfully'})
    elif request.method == "DELETE":
        show = Show.query.filter_by(id=id).first()
        if not show:
            return jsonify({'message':'No such show exists.'})
        db.session.delete(show)
        db.session.commit()
        return jsonify({"message":"Show deleted successfullly!"})
