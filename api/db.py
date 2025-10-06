import sqlite3
from datetime import datetime
import logging
import click
import json
from api import essolution
from werkzeug.security import generate_password_hash
from flask import current_app, g

__author__ = 'Elijah Siaw (Es Solution LTD)'
log = logging.getLogger(__name__)
def Esblog_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
user = None
def init_db(mode):
      log.info(f'Running in {mode} mode')
      db = Esblog_db()
      settings = essolution.config(Esblog_db)
      log.info('Creating tables')
      try:
        if mode == 'dev':
          with current_app.open_resource('dev.sql') as f:
            db.executescript(f.read().decode('utf8'))
            settings.add_init_user({'email':'admin@essolution.com', 'fullname':'Admin Elijah', 'password':'test123', 'role':'admin'})
        else:
          with current_app.open_resource('prod.sql') as f:
            with open(current_app.config["INIT_USER_PATH"]) as file:
              global user
              user = json.load(file)
              log.info("Loading users........")
              db.executescript(f.read().decode('utf8'))
              settings.add_init_user(user)
      except sqlite3.OperationalError as e:
         log.warn(e)
         settings.add_init_user(user)
      with open(current_app.config["INIT_BLOG_PATH"]) as file:
        posts = json.load(file)
        settings.load_init_posts(posts)
      with open(current_app.config["INIT_COMMENT_PATH"]) as file:
        comments = json.load(file)
        settings.load_init_comments(comments)
      with open(current_app.config["INIT_PROJECTS_PATH"]) as file:
        projects = json.load(file)
        settings.load_init_projects(projects)
       

@click.command('init-db')
@click.option('--mode', default='dev', help='The setup mode (dev or prod).')
def init_db_command(mode):
    """Clear the existing data and create new tables."""
    click.echo('Initializing database')
    init_db(mode)
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    