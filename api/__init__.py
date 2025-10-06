import os
import logging
import traceback
import secrets
from flask import Flask, render_template, request, make_response, redirect
from flask_caching import Cache
from werkzeug.exceptions import HTTPException
import jinja2
from datetime import datetime, timedelta, UTC
from api import essolution
from . import time_util
log = logging.getLogger(__name__)
__author__ = 'Elijah Siaw (Es Solution LTD)'
cache = Cache()
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(32),
        #Database url
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
        INIT_USER_PATH=os.path.join(app.instance_path, 'data/users.json'),
        INIT_COMMENT_PATH=os.path.join(app.instance_path, 'data/comments.json'),
        INIT_BLOG_PATH=os.path.join(app.instance_path, 'data/blogs.json'),
        INIT_PROJECTS_PATH=os.path.join(app.instance_path, 'data/projects.json'),
        API_KEY="TKey_8f1b18afab5edf21b688f481db320c933880b5c1f0464ae15d514981c31442e2", #In production save it in environmental variable and retrieve using ``os.environ.get("API_KEY")``
        MAX_CONTENT_LENGTH = 20*1000*1000,
        CACHE_TYPE= "SimpleCache",  # Flask-Caching related configs
        CACHE_DEFAULT_TIMEOUT=300
        )
    logging.basicConfig(level=logging.DEBUG)

    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info(' Portfolio App Starting')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    log.info('Trying to load testapp/config.py...')
    try: 
      if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
      else:
        # load the test config if passed in
        log.info('Local config loaded')
        app.config.from_mapping(test_config)
    except Exception:
        log.info('Config not found or invalid')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    #cache object
    log.info('Setting up cache')
    cache.init_app(app)
    init_db(app)
    #init_data(app)
    init_templating(app)
    init_app_behaviours(app)
    register_blueprints(app)
    
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info(' Startup Complete!')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    @app.route('/') # handles home page
    def home():
      user = essolution.models.get_users()
      projects = essolution.models.load_projects()
      return render_template('index.html', user=user, projects=projects)
      
    @app.route('/about') # handles about page
    def about():
      user = essolution.models.get_users()
      posts = essolution.models.load_posts()
      comments = essolution.models.get_comments()
      return render_template('about.html', user=user, posts=posts, comments=comments, page=None)
    
    @app.route('/about/<path:slug>') # handles about page
    def more(slug):
      users = essolution.models.get_users()
      posts = essolution.models.load_posts()
      comments = essolution.models.get_comments()
      return render_template('about.html', users=users, posts=posts, comments=comments, page=slug)
      
    @app.route('/api/theme')
    def change_theme():
      theme = request.args.get('theme')
      expiredin = datetime.now(UTC) + timedelta(days=730)
      res = make_response({'message': 'Theme changed'})
      res.set_cookie('x-es-theme', theme, 'max_age', expiredin)
      return res
        
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if not hasattr(e, 'code'):
            return catch_all(e)

        if e.code >= 300 and e.code < 400:
            return redirect(e.new_url, e.code)

        return render_template('exceptions/http_exception.html', e=e), e.code

    @app.errorhandler(Exception)
    def catch_all(e):
        title = str(e)
        message = traceback.format_exc()

        log.error('Exception caught: %s\n%s' % (title, message))

        return render_template('exceptions/error_page.html', title=title, message=message, preformat=True)
        
    return app

def init_db(app):
    from . import db
    db.init_app(app)
    log.info('Using database: "%s"' % db.Esblog_db)

def init_templating(app):
  log.info('Setting up templating environment')
  app.jinja_env.filters['format_datetime'] = time_util.format_datetime
  app.jinja_env.filters['format_date'] = time_util.format_date
  app.jinja_env.filters['format_date_long'] = time_util.format_date_long
  app.jinja_env.filters['format_datetime_long'] = time_util.format_datetime_long
  app.jinja_env.filters['format_datetime_short'] = time_util.format_datetime_short
  
  # Don't allow output of undefined variables in jinja templates
  app.jinja_env.undefined = jinja2.StrictUndefined


def init_app_behaviours(app):
    @app.context_processor
    def add_global_context():
        cache.clear()
        theme = request.cookies.get('x-es-theme')
        return {'current_year': datetime.now(), 'theme': theme}
        
def register_blueprints(app):
    log.info('Registering blueprints')
    from . import auth
    app.register_blueprint(auth.bp)
    from . import blog
    app.register_blueprint(blog.bp)
    from . import api 
    app.register_blueprint(api.bp)
    from . import dashboard 
    app.register_blueprint(dashboard.bp)