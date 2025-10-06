import functools
from api import essolution
from flask import (
    Blueprint, flash, redirect, render_template, session, request, jsonify, abort, url_for, current_app
)
from flask_cors import cross_origin
import requests
import json
from uuid import uuid4
from api.auth import verify_token

bp = Blueprint('api', __name__, url_prefix='/api') #handles api calls
@bp.route('/message', methods=['POST'])
#send email message
@cross_origin(origins=['https://api.essolution.dev', 'http://localhost:5000'], methods=['POST'], support_credentials=True)
def message():
    try:
      data = {"name":request.form["fullname"],"email":request.form["email"],"org":request.form["org"],"position":request.form["position"],"message":request.form["message"]}
      # replacr this with your email to recieve mails
      sender = 'elijahsiaw@gmail.com'
     # api_url = "https://api.essolution.dev/v3/mail"
      api_url = f"http://localhost:3000/v3/mail?sender={sender}"
      #set the API KEY headers
      headers = {'APIKEY':current_app.config['API_KEY']}
        # Send the POST request with the data as a JSON payload
      response = requests.post(api_url, headers=headers, json=data)
      
      response.raise_for_status()

        # convert response to python dict
      res = response.json()
        # Return the API's response message
      flash(res['message'],'message')
      return redirect(url_for('home'))

    except requests.exceptions.RequestException as e:
        flash(f'Failed to send message {e}')
        abort(500)
        
@bp.route('/post', methods=['POST'])
@verify_token
#send blog post
@cross_origin(origins=['https://api.essolution.dev', 'http://localhost:5000'], methods=['POST'], support_credentials=True)
def post():
  try:

      image = str(request.files.get("image").read()) if request.files.get("image").filename.endswith(".svg") else essolution.base64_url(request.files.get("image"))

      video = essolution.base64_url(request.files.get("video"), "video")
      
      api_url = "https://api.essolution.dev/v3/markup"
      
      '''
      set the API KEY headers
      Get the api key at https://essolution.dev/api
      '''
      headers = {'APIKEY':current_app.config['API_KEY']}
      
      post = {"post": request.form.get("post")}
    # Send the POST request to the url to convert the markdown to html
      response = requests.post(api_url, headers=headers, json=post)
      
        # raise a http error status if an error occurs
      
      response.raise_for_status()

        # convert response to python dict
      post = response.json()
      # add response data to dict
      data = {"title":request.form.get("title"),"tag":request.form.get("tag"),"image":image,"video":video,"slug":str(uuid4()),"draft":request.form.get("draft"),"summary":request.form.get("summary"),"post":post["html"], "authors":session["user_id"], "prev":json.dumps({
        "prevtitle": request.form.get("prevtitle"),
        "prevlink": request.form.get("prevlink")
      }),"next":json.dumps({
        "nexttitle": request.form.get("nexttitle"),
        "nextlink": request.form.get("nextlink")
      })}
      
      if request.form['prevlink']:
        #find previous post and update its next navigation
        prev_post = essolution.models.find_post(request.form['prevlink'])
        next_navigation = {
        "next":json.dumps({
        "nexttitle": request.form.get("title"),
        "nextlink": request.form.get("tag")
      })
      }
      essolution.models.update_post(prev_post['id'], next_navigation)
      #save it in database
      essolution.models.create_post(data)
        # Return the API's response message
      flash('Post created successfully','message')
      return redirect(url_for('blog.post', slug=data['tag']))

  except requests.exceptions.RequestException as e:
        flash(f'Failed to create post {e}', 'error')
        abort(500)

@bp.route('/post/<int:id>/update', methods=['POST'])
@verify_token
#update blog post
@cross_origin(origins=['https://api.essolution.dev', 'http://localhost:5000'], methods=['POST'], support_credentials=True)
def update(id):
  try:
    image = str(request.files.get("image").read()) if request.files.get("image").filename.endswith(".svg") else essolution.base64_url(request.files.get("image"))

    video = essolution.base64_url(request.files.get("video"),"video")
      
    api_url = "https://api.essolution.dev/v3/markup"
    
    '''
      set the API KEY headers
      Get the api key at https://essolution.dev/api
    '''
    headers = {'APIKEY':current_app.config['API_KEY']}
      
    post = {"post": request.form.get("post")}
    # Send the POST request to the url to convert the markdown to html
    response = requests.post(api_url, headers=headers, json=post)
      
        # raise a http error status if an error occurs
      
    response.raise_for_status()

        # convert response to python dict
    post = response.json()
      # add response data to dict
    data = {"title":request.form.get("title"),"tag":request.form.get("tag"),"image":image,"video":video,"slug":str(uuid4()),"draft":request.form.get("draft"),"summary":request.form.get("summary"),"post":post["html"], "authors":session["user_id"], "prev":json.dumps({
        "prevtitle": request.form.get("prevtitle"),
        "prevlink": request.form.get("prevlink")
      }),"next":json.dumps({
        "nexttitle": request.form.get("nexttitle"),
        "nextlink": request.form.get("nextlink")
      })}
      
    # find previous post and update its next navigation
    if request.form['prevlink']:
      prev_post = essolution.models.find_post(request.form['prevlink'])
      next_navigation = {
        "next":json.dumps({
        "nexttitle": request.form.get("title"),
        "nextlink": request.form.get("tag")
      })
      }
      essolution.models.update_post(prev_post['id'], next_navigation)
    # update the database
    essolution.models.update_post(id,data)
    flash('Post updated successfully','message')
    return redirect(url_for('blog.post',slug=data['tag']))
  except Exception as e:
    flash(f'Error: failed to update post {e}','error')
    return redirect(url_for('dashboard.update',id=data['tag']))
    
@bp.route('/project', methods=['POST'])
#create project
@verify_token
@cross_origin(origins=['https://api.essolution.dev', 'http://localhost:5000'], methods=['POST'], support_credentials=True)
def project():
  try:
    image = str(request.files.get("src").read()) if request.files.get("src").filename.endswith(".svg") else essolution.base64_url(request.files.get("src"))
    builtwith = request.form.get("builtwith").split(',')
    data = {"title":request.form.get("title"),"platform":request.form.get("platform"),"description":request.form.get("description"), "url":request.form.get("url"), "src":image,"repo":request.form.get("repo"),"builtwith":builtwith}
      #save it in database
    essolution.models.create_project(data)
        # Return the API's response message
    flash('Project created successfully','message')
    return redirect(url_for('dashboard.projects'))
  except Exception as e:
    flash(f'Failed to create projects {e}', 'error')
    return redirect(url_for('dashboard.create_post'))
        
@bp.route('/project/<string:id>/update', methods=['POST'])
#update project
@verify_token
@cross_origin(origins=['https://api.essolution.dev', 'http://localhost:5000'], methods=['POST'])
def update_project(id):
  try:
    image = str(request.files.get("src").read()) if request.files.get("src").filename.endswith(".svg") else essolution.base64_url(request.files.get("src"))
    builtwith = request.form.get("builtwith").split(',')
    data = {"title":request.form.get("title"),"platform":request.form.get("platform"),"description":request.form.get("description"), "url":request.form.get("url"), "src":image,"repo":request.form.get("repo"),"builtwith":json.dumps(builtwith)}
    # check if project exists
    if not essolution.models.project_exists(id):
      flash('Project does not exist', 'error')
      return redirect(url_for('dashboard.projects'))
    # update the database
    essolution.models.update_project(id,data)
    flash('Project updated successfully','message')
    return redirect(url_for('dashboard.projects'))
  except Exception as e:
    flash(f'Error: failed to update project {e}','error')
    return redirect(url_for('dashboard.update_project', project=id))