#!/bin/bash
flask --app api  init-db --mode dev
flask --app api run --debug
cat setup.log