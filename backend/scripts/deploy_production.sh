#!/bin/bash
BASE="/home/website/"
SRC="${BASE}source/my-property-consultants/"
ENV="${BASE}Env/env/"
WEB="${BASE}www/"
UWSGI_INI="/etc/uwsgi/sites/website.ini"
NGINX_CACHE="/var/cache/nginx/"
PAGESPEED_CACHE="/var/cache/ngx_pagespeed/"
. "${ENV}bin/activate"
cd $SRC && git pull
cp -rf ${SRC}* $WEB
cd $WEB
python manage.py collectstatic --noinput && python manage.py migrate && touch $UWSGI_INI
find $NGINX_CACHE -type f -delete
find $PAGESPEED_CACHE -type f -delete
