from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from jinja2.exceptions import TemplateNotFound
import json
import os
from api import cache, essolution
from api.auth import protected, verify_token

bp = Blueprint('blog', __name__)

def load_comments(id):
      return essolution.models.get_comment_by_path(id)
      
@bp.route('/blog')
def index():
    posts = essolution.models.load_posts()
    return render_template('blog/index.html', posts=posts)

@bp.route('/blog/<path:slug>',methods=('POST', 'GET', 'PUT')) # handles all other blog pages
@verify_token
def post(slug):
  error = None
  posts = get_post(slug, check_author=False)
  prev = json.loads(posts['prev']) if posts['prev'] else None
  next = json.loads(posts['next']) if posts['next'] else None
  
  comments = load_comments(slug)
  if request.method == 'POST':
    try:
      if not g.user:
        flash("Log in to add a comment", "error")
        return redirect(url_for('blog.post', slug=slug))
      data = request.form.get("message")
      if not data:
        flash("Comment required", "error")
        return redirect(url_for('blog.post', slug=slug))
      payload = {
        "name": g.user['fullname'],
        "message": data,
        "path": slug
      }
      
      essolution.models.add_comments(payload)
      return redirect(f'/blog/{slug}#comments')
    except Exception as e:
      return f'Error: {e}', 500
  
  if request.method == 'PUT':
    try:
      if not g.user:
        error="Log in to add a reaction"
      data = request.json
      if not data:
        error = "Reaction required"
      for comment in comments:
        if comment["userId"] == data["userId"]:
          comment[data["reaction"]]  = int(comment[data["reaction"]])+1
          essolution.models.add_reaction(data["userId"], comment[data["reaction"]], data["reaction"])
      return render_template(f'blog/{slug}/index.html', posts=posts, comments=comments)
      flash(error, 'error')
      return render_template(f'blog/{slug}/index.html', posts=posts, comments=comments) 
    except Exception as e:
     return f"Error: {e}", 500
  try:
    return render_template('blog/post.html', post=posts, comments=comments,prev=prev,next=next)
  except TemplateNotFound:
    try:
      return render_template(f'blog/{slug}.html', posts=posts, comments=comments)
    except TemplateNotFound:
        abort(404)

@cache.memoize(50) 
def get_post(id, check_author=True):
  '''
    if id.startswith('flask'):
      return False
  '''
  post = essolution.models.find_post(id)
  if post is None:
        abort(404, f"Post id {id} doesn't exist.")

  if check_author and post['author'] != g.user['id']:
        abort(403)

  return post