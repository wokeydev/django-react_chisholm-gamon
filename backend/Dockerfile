FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y gdal-bin python-gdal python3-gdal
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt
RUN apt-get purge -y --auto-remove gcc build-essential
ADD . /code/

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
WORKDIR /code/static_src/build
WORKDIR /code
CMD ["C_FORCE_ROOT=1" ,"celery",  "-A", "sportscard_api", "worker", "--loglevel=info"]
