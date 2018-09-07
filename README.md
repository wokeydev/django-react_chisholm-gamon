# Chisholm & Gamon

### Description

Real Estate website for Chisholm & Gamon. Built by TechEquipt, Real Estate data by AgentBox. Launch 2018

### Requirements

- Docker
- Docker Compose

### Backend Platform

- Django 2.1
- Python 3.6
- Nginx
- Postgres
- Gulp

### Frontend Platform

- Next.js

Note: All platform requirements will be managed in the container

### Getting started

#### Starting a local server

`git clone <REPO>`
`docker-compose up`

Migrate:
`docker-compose run web python manage.py migrate`

Create a superuser:
`docker-compose run web python manage.py createsuperuser`

Create Migrations:
`docker-compose run web python manage.py makemigrations`

Update requirements (with the container running)
`docker-compose exec web pip install -r requirements.txt`

#### Frontend Development

TODO: Frontend info

##### to install local npm requirements:

- navigate to folder "/static_src/build"
- run `npm install`

##### to compile assets:

- navigate to folder "/static_src/build"
- run `gulp` to build once
- run `gulp watch` to watch for SASS/JS changes and compile as you save changes

#### Creating pull requests

- stop any running build process - eg `gulp`
- run `docker-compose exec web python manage.py collectstatic` to push project static files to nginx proxy location
- push your local commit(s) to the remote feature branch
- create a pull request from that branch to the one you want to merge into, eg master

#### General Notes

- Wagtail has FontAwesome 4.7 icons for streamfields etc. See https://fontawesome.com/v4.7.0/icons/
# django-react_chisholm-gamon
# django-react_chisholm-gamon
