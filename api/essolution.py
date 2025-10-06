# coding=utf-8
import logging
import traceback
import json
from base64 import  b64encode
from werkzeug.security import generate_password_hash
from api import db as Esdb
from flask import redirect, url_for, flash
log = logging.getLogger(__name__)

__author__ = 'Elijah Siaw (Es Solution LTD)'


print_stack_traces = False

class portfolio_actions:
  def __init__(self, db):
    self.db = db
    
  def add_reactions(self,comId, reaction, value):
    try:
      self.db().execute(f"UPDATE comments SET {reaction} = ? WHERE id = ?",(value, comId))
      self.db().commit()
    except self.db.IntegrityError as e:
      log.warn(f"Error: {e}")
  
  def get_comment_by_path(self, path):
    comments = self.db().execute("SELECT * FROM comments WHERE path = ?",(path,))
    return comments
  
  def find_comment(self,comId):
    comments = self.db().excute("SELECT * FROM comments WHERE id = ?",(comId,)).fetchone()
    return dict(comments) if comments else comments
  
  def get_comments(self):
    comments = self.db().execute("SELECT * FROM comments")
    return comments
    
  def delete_comment(self, comId):
    try:
      self.db().execute("DELETE FROM comments WHERE id = ?", (comId,))
      self.db().commit()
    except Exception as e:
      log.warn(f"Error: {e}.")
    
  def add_comments(self,comment):
    try:
      self.db().execute("INSERT INTO comments (name, message, path) VALUES (?, ?, ?)",(comment["name"],comment["message"],comment["path"]))
      self.db().commit()
    except self.db().IntegrityError as e:
      log.warn(f"Error: {e}.")

  def create_post(self,post):
    self.db().execute('INSERT INTO posts (title,tag,slug,image,video,summary,post, authors, draft,next,prev) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(post["title"],post["tag"],post["slug"],post["image"],post["video"],post["summary"],post["post"],post["authors"],post["draft"],post["next"],post["prev"]))
    self.db().commit()
  
  
  def find_post(self, postId):
    post = self.db().execute(
        'SELECT * FROM posts'
        ' WHERE tag = ?',
        (postId,)).fetchone()
    return dict(post) if post else post
  
    
  def load_posts(self):
    posts = self.db().execute('SELECT * FROM posts')
    return posts
    
  def update_post(self,postId, post):
    try:
      for k,v in post.items():
        self.db().execute(f'UPDATE posts SET {k} = ? WHERE id = ?',(v, postId))
        self.db().commit()
    except self.db().IntegrityError:
      log.warn("Failed to update post.")
      
  def delete_post(self, postId):
    self.db().execute('DELETE FROM posts WHERE tag = ?', (postId,))
    self.db().commit()
    
  def add_user(self,email, fullname, password):
    log.info('Creating user \'%s\'' % (email))
    
    existing_user = self.user_exists(email)
    if existing_user:
        log.info('User already exists')
        flash('User already exists', 'error')
        return False
    try:
      self.db().execute(
        "INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",(fullname, email,generate_password_hash(password)))
      self.db().commit()
    except self.db().IntegrityError:
                log.warn(f"User {fullname} is already registered.")
    else:
      return redirect(url_for("auth.login"))        
    
  def update_user(self,userId, users):
    try:
      for k,v in users.items():
        self.db().execute(f"UPDATE users SET {k} = ? WHERE id = ?",(v, userId))
        self.db().commit()
    except self.db().IntegrityError:
      log.warn("Failed to update user.")
  def delete_user(userId):
   return

  
  def user_exists(self, email):
    user = self.db().execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
    return bool(user)
  
  
  def get_user(self,email):
    db = self.db()
    user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    return user
  
  
  def get_users(self):
    db = self.db()
    users = db.execute(
            'SELECT * FROM users').fetchone()
    return users
  
  
  def get_user_byId(self,userId):
    db = self.db()
    user = db.execute(
            'SELECT * FROM users WHERE id = ?', (userId,)).fetchone()
    return user
    
  def create_project(self,project):
    self.db().execute('INSERT INTO projects (platform,title,description, url,src,repo,builtwith) VALUES (?, ?, ?, ?, ?, ?, ?)',(project["platform"],project["title"],project["description"],project.get("url"),project["src"],project.get("repo"),json.dumps(project["builtwith"])))
    self.db().commit()
  
  
  def find_project(self, projectId):
    project = self.db().execute(
        'SELECT * FROM projects'
        ' WHERE id = ?',
        (projectId,)).fetchone()
    project = dict(project)
    project['builtwith'] = json.loads(project['builtwith'])
    return project
  
    
  def load_projects(self):
    projects = self.db().execute('SELECT * FROM projects')
    data = list()
    for project in projects:
      project = dict(project)
      project['builtwith'] = json.loads(project['builtwith'])
      data.append(project)
    return data
    
  def update_project(self,projectId, project):
    try:
      for k,v in project.items():
        self.db().execute(f'UPDATE projects SET {k} = ? WHERE id = ?',(v, projectId))
        self.db().commit()
    except self.db().IntegrityError:
      log.warn("Failed to update post.")
      
  def delete_project(self, projectId):
    self.db().execute('DELETE FROM projects WHERE id = ?', (projectId,))
    self.db().commit()
    
  def post_exists(self, slug):
    post = self.db().execute(
            'SELECT * FROM posts WHERE slug = ?',(slug,)
        ).fetchone()
    return bool(post)
  
  
  def comment_exists(self, comId):
    post = self.db().execute(
            'SELECT * FROM comments WHERE id = ?',(comId,)
        ).fetchone()
    return bool(post)
    
  def project_exists(self, slug):
    project = self.db().execute(
            'SELECT * FROM projects WHERE id = ?',(slug,)
        ).fetchone()
    return bool(project)
  
models = portfolio_actions(Esdb.Esblog_db)


class config(portfolio_actions):
  def __init__(self, db):
    self.db = db
    super().__init__(db)
  def add_init_user(self, user):
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info('Creating user \'%s\'' % (user.get('fullname')))
    log.info('Log in info')
    log.info('Email: \'%s\' and Password: \'%s\'' % (user.get('email'),user.get('password')))
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    existing_user = super().user_exists(user.get('email'))
    if existing_user:
        log.info('User already exists')
        return False
    self.db().execute(
        "INSERT INTO users (fullname,email,password,phone,education,address,occupation,company,website,country,bio,role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(user.get('fullname'), user.get('email'),generate_password_hash(user.get('password')),user.get('phone'),user.get('education'),user.get('address'),user.get('occupation'),user.get('company'),user.get('website'),user.get('country'), user.get('bio'), user.get('role')))
    self.db().commit()

  def load_init_posts(self, posts):
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info('Loading initial posts')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    for post in posts:
      existing_post = super().post_exists(post["slug"])
      if not existing_post:
        log.info('loading \'%s\' into database',(post["title"]))
        self.db().execute('INSERT INTO posts (title,tag,slug,image,video,thumbnail,summary,post, authors,next,prev,datecreated,dateupdated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(post["title"],post["tag"],post["slug"],post["image"],post["video"],post["thumbnail"],post["summary"],post["post"],post["authors"],json.dumps(post["next"]),json.dumps(post["prev"]),post["datecreated"],post["dateupdated"]))
        self.db().commit()
  
  def load_init_comments(self, comments):
      log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
      log.info('Loading initial post comments')
      log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
      total = len(comments)
      for comment in comments:
        existing_comments = super().comment_exists(comment["id"])
        if not existing_comments:
          log.info('loaded \'%s\'  of \'%s\' comments into database' % (comment["id"], total))
          self.db().execute('INSERT INTO comments (name,message,path,loves,likes,dislikes,datecreated,dateupdated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',(comment["name"], comment["message"],comment["path"],comment["loves"],comment["likes"],comment["dislikes"],comment["datecreated"],comment["dateupdated"]))
          self.db().commit()
  def load_init_projects(self, projects):
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info('Loading initial projects')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    for project in projects:
      existing_project = super().project_exists(project["id"])
      if not existing_project:
        log.info('loading \'%s\' into database',(project["title"]))
        self.db().execute('INSERT INTO projects (platform,title,description, url,src,repo,builtwith) VALUES (?, ?, ?, ?, ?, ?, ?)',(project["platform"],project["title"],project["description"],project.get("url"),project["src"],project.get("repo"),json.dumps(project["builtwith"])))
        self.db().commit()

def base64_url(file, media_type="image"):
    if file:
      if '.' in file.filename:
        ext = file.filename.rsplit('.',1)[1]
        data_url = f"data:{media_type}/{ext};base64,{b64encode(file.read()).decode('utf-8')}"
        return data_url
      return ''
    return ''
