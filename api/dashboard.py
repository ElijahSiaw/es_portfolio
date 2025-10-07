from flask import (
    Blueprint, flash, g, redirect, session, render_template, request, url_for
)
from werkzeug.exceptions import abort
from jinja2.exceptions import TemplateNotFound
import json
import os
from api import cache, essolution
from api.auth import verify_token

bp = Blueprint('dashboard', __name__)

def load_comments(id):
      return essolution.models.get_comment_by_path(id)
      
@bp.route('/dashboard')
#main dashboard page
@verify_token
def index():
    posts = essolution.models.load_posts()
    comments = essolution.models.get_comments()
    return render_template('dashboard/index.html', page=None, posts=posts, comments=comments), 200
        
@bp.route('/dashboard/create', methods=['GET'])
@verify_token
@cache.cached(timeout=50)
def create():
    return render_template('dashboard/create.html', post=None), 200
    
@cache.memoize(50)    
def get_post(id, check_author=True):
    post = essolution.models.find_post(id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['authors'] != g.user['id']:
        abort(403)

    return dict(post)
    
@bp.route('/dashboard/<path:id>/update', methods=['GET'])
@verify_token
def update(id):
    post = get_post(id)
    post['prev'] = json.loads(post.get('prev'))
    post['next'] = json.loads(post.get('next'))
    return render_template('dashboard/create.html', post=post), 200
    
@bp.route('/dashboard/<path:id>/delete', methods=['GET'])
@verify_token
def delete(id):
    post = essolution.models.find_post(id)
    if not post:
      flash('Post does not exist', 'error')
      return redirect(url_for('dashboard.post', slug='posts'))
    if post['prev']:
      post['prev'] = json.loads(post['prev'])
      prev_post = essolution.models.find_post(post['prev'].get('prevlink'))
      next_navigation = {
        "next":post.get("next")
      }
      if prev_post:
        essolution.models.update_post(prev_post['id'], next_navigation)
    if post.get('next'):
      post['next'] = json.loads(post['next'])
      next_post = essolution.models.find_post(post['next'].get('nextlink'))
      prev_navigation = {
        "prev":json.dumps(post.get("prev"))
      }
      if next_post:
        essolution.models.update_post(next_post['id'], prev_navigation)
    essolution.models.delete_post(id)
    cache.delete_memoized(get_post)
    return redirect(url_for('dashboard.post', slug='posts'))

@bp.route('/dashboard/comment/<int:id>/delete', methods=['GET'])
@verify_token
def comment(id):
    if not essolution.models.comment_exists(id):
      flash('Comment already deleted', 'error')
      return redirect(url_for('dashboard.post', slug='comments'))
    essolution.models.delete_comment(id)
    cache.delete_memoized(post, 'comments')
    return redirect(url_for('dashboard.post', slug='comments'))
    
@bp.route('/dashboard/<path:slug>', methods=['GET','POST']) # handles all other dashboard pages
@verify_token
def post(slug):
  try:
    data = None
    if request.method=='POST':
      image = essolution.base64_url(file=request.files.get("user-photo"))
      cover = essolution.base64_url(file=request.files.get("user-cover-photo"))

      if image:
        data={
          "image":image
        }
        essolution.models.update_user(session['user_id'], data)
        
        return redirect(url_for('dashboard.post', slug=slug))
      if cover:
        data={
          "cover":cover
        }
        essolution.models.update_user(session['user_id'], data)
        
        return redirect(url_for('dashboard.post', slug=slug))
      
      essolution.models.update_user(session["user_id"], request.form)
      
      return redirect(url_for('dashboard.post', slug=slug))
      
    posts = essolution.models.load_posts()
    comments = essolution.models.get_comments()
    return render_template('dashboard/index.html', page=slug, posts=posts,comments=comments),200
  except TemplateNotFound:
        abort(404, 'Page not found')
@bp.route('/projects', methods=['GET'])
@verify_token
def projects():
  projects = essolution.models.load_projects()
  return render_template('dashboard/projects.html', projects=projects)
  
@bp.route('/projects/create', methods=['GET'])
@verify_token
def create_project():
  return render_template('dashboard/create_project.html', project=None),200
  
@bp.route('/projects/<int:slug>/update', methods=['GET'])
@verify_token
def update_project(slug):
  project = essolution.models.find_project(slug)
  return render_template('dashboard/create_project.html', project=project), 200
  
@bp.route('/projects/<int:slug>/delete', methods=['GET'])
@verify_token
def delete_project(slug):
  if not essolution.models.project_exists(slug):
    flash('Project does not exist', 'error')
    return redirect(url_for('dashboard.projects'))
  flash('Project deleted successfully', 'error')
  essolution.models.delete_project(slug)
  return redirect(url_for('dashboard.projects'))
