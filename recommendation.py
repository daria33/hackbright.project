from flask import Flask, render_template, redirect, request, session, flash, url_for
import model
from flask_oauth import OAuth
import os

#This section is necessary to connect with facebook
oauth = OAuth()

consumer_keys = os.environ.get("app_id")
consumer_secrets = os.environ.get("app_secret")

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=consumer_keys,
    consumer_secret=consumer_secrets,
    request_token_params={'scope': 'email'}
)

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'

#This route maps doctors
@app.route("/")
def index():

    coordinates = model.getlonlat()
    
    return render_template("input.html", coordinates = coordinates, consumer_secrets = consumer_secrets)


#Takes you to the facebook authentication page, send you and response on to next route
@app.route('/login')
def login():
    print "in login!!!"
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))
    

#how do you get it to print the doctors name?
@app.route('/ratings/<idd>')
def show_ratings(idd):

    ratings = model.session.query(model.Rating).filter(model.Doctor.id == idd).first()
    rating = ratings.rating
    review = ratings.review
    # print rating.Doctor.name
    return render_template("name.html", rating=rating, review=review, idd=id)


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    print "in authorized"
    #when would this ever happen?
    if resp is None:
        flash("Facebook authentication error.")
        print "no data!"
        return redirect('/')

    session['logged_in'] = True
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    user = add_new_user()
    session['user'] = user.id

    flash("You are logged in %s." % (me.data['first_name']))

    return redirect('/')

def add_new_user():
    """ Uses FB id to check for exisiting user in db. If none, adds new user."""

    #names facebook me object as fb_user
    fb_user = facebook.get('/me').data

    #queries database comparing user id with the ids in users table
    existing_user = model.session.query(model.User).filter(model.User.facebook_id == fb_user['id']).first()

    if existing_user is None:
        new_user = model.User()
        new_user.facebook_id = fb_user['id']
        new_user.first_name = fb_user['first_name']
        new_user.email = fb_user['email']

        # commit new user to database
        model.session.add(new_user)
        model.session.commit()
        # Go get that new user
        new_user = model.session.query(model.User).filter(model.User.facebook_id == fb_user['id']).first()
        return new_user
    
    else:
        return existing_user

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route("/logout")
def logout():
    clear_session()
    flash("Successfully logged out.")
    return redirect('/')

#but this doesn't log you out of facebook, how do you do that?
@app.route('/clearsession')
def clear_session():
    session['logged_in'] = False
    session['oauth_token'] = None
    session['user'] = None
    return 

@app.route('/addreview')
def add_review():
    new_rating = model.Rating()

    new_rating.doctor_id = 60
    new_rating.user_id = 1
    new_rating.review = "Even Greater!"
    new_rating.rating = 4

    # commit new user to database
    model.session.add(new_rating)
    model.session.commit()
    return redirect("/")

# @app.route('/adddoc')
# def add_doc():
#     new_doc = model.Doctor()

#     new_doc.name = ?
#     new_doc.cert = ?
#     new_doc.business_name = ?
#     new_doc.address = ?
#     new_doc.suite = ?
#     new_doc

#     id = Column(Integer, primary_key=True)
#     name = Column(Unicode(100), nullable=False)
#     cert = Column(Unicode(50), nullable=True)
#     business_name = Column(Unicode (100), nullable=True)
#     address = Column(Unicode(500), nullable=False)
#     suite = Column(Unicode(500), nullable=True)
#     phone_number = Column(Unicode(25), nullable=True)
#     recommended_by = Column(Unicode(50), nullable=False)
#     gender = Column(Unicode(15), nullable=True)
#     lat = Column(Float(50), nullable=True)
#     lon = Column(Float(50), nullable=True)
#     specialties = Column(Unicode(500), nullable=True)
#     pub_insurance = Column(String(25), nullable=True)


if __name__== "__main__":
    app.run(debug = True)