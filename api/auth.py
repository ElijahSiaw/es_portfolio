import functools
from api import essolution
from flask import (
    Blueprint, flash, g, redirect, render_template, request, jsonify, session, url_for, current_app, make_response
)
import datetime
from urllib.parse import quote, unquote
from werkzeug.security import check_password_hash, generate_password_hash
import os
import jwt
import json

bp = Blueprint('auth', __name__, url_prefix='/account')
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        error = None
        
        if not fullname:
            error = 'Full name is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'

        if error is None:
          essolution.models.add_user(email=email, password=password, fullname=fullname)
          flash('Registration successful', 'message')
          return redirect(url_for('auth.login'))
          
        flash(error, 'error')
    return render_template('account/signup.html')

@bp.route('/login', methods=('GET', 'POST'))
@verify_token
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = essolution.models.get_user(email)

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            returnurl = request.args.get('returnurl')
            
            res= make_response(redirect(url_for('dashboard.post', slug=unquote(returnurl)))) if returnurl else make_response(redirect(url_for('home')))
            expiredin = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
            payload = {
        'user_id': user["id"],
        'exp': expiredin  # Token expiration time
         }
         # Sign the token using the secret key
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            res.set_cookie('es-se-state', token, 'max_age', expiredin)
            return res, 200
        flash(error, 'error')
    if request.user:
      return redirect(url_for('home'))
    return render_template('account/login.html')
  
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = essolution.models.get_user_byId(user_id)
        
@bp.route('/logout')
def logout():
    session.clear()
    res = make_response(redirect(url_for('auth.login')))
    res.delete_cookie('es-se-state')
    return res, 200
    
def verify_token(f):
    """
    Decorator to verify a token before allowing access to a route.
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        request.user = None
        request.comments = None
        # Check for 'cookies' in  header
        token = request.cookies.get('es-se-state')
        if not token:
            return f(*args, **kwargs)
        try:
            # Decode and verify the token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            # check if user exists in database
            
            user = essolution.models.get_user_byId(data['user_id'])
            if not user:
              return redirect(url_for('auth.logout'))
            request.user = user
        except jwt.ExpiredSignatureError:
            return redirect(url_for('auth.logout'))
        except jwt.InvalidTokenError:
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    return decorated 

def protected(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', returnurl=quote(request.path.replace("/dashboard","",1), safe="")))
        return view(**kwargs)
    return wrapped_view
