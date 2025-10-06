# coding=utf-8
import logging
import traceback
import os
import json
from werkzeug.security import generate_password_hash
from api.essolution import models
log = logging.getLogger(__name__)

__author__ = 'Elijah Siaw (Es Solution LTD)'

print_stack_traces = False

def init_data(app):
    log.info('Initializing Users')
    add_init_user('admin@essolution.com', 'Admin', 'test123')
    
    
    log.info('Initializing comments')
    load_init_comments(app)
    
def load_init_comments(app):
  path = app.config['INIT_COMMENT_PATH']
  #check if file exist
  if not os.path.exists(path):
    log.warn('Comments data missing')
  else:
    log.info('Reading comments data')
    with open(path, 'r') as file:
      comments = json.load(file)
      for comment in comments:
        models.add_comments(author=comment["author"], message=comment["message"], loves=comment["loves"], likes=comment["likes"],dislikes=comment["dislikes"], datecreated=comment["datecreated"], dateupdated=comment["dateupdated"])
      log.info('Complete')
      
def add_init_user(email, fullname, password):
    log.info('Creating user \'%s\'' % (email))
    
    existing_user = False
    if existing_user:
        log.info('User already exists')
        #flash('User already exists', 'error')
        return False
    models.db().execute(
        "INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",(fullname, email,password))
    models.db().commit()