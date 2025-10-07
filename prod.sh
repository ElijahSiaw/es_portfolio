#!/bin/bash
flask --app api  init-db --mode prod
gunicorn --bind 127.0.0.1:5000 wsgi:app
cat setup.log