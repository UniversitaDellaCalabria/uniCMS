FROM python:3.10-slim-buster
MAINTAINER Francesco Filicetti <francesco.filicetti@unical.it>

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
RUN pip install --upgrade pip

# install dependencies
RUN apt-get update \
    && apt-get install -y poppler-utils git locales xmlsec1 gcc \
                          libmagic-dev libssl-dev \
                          default-libmysqlclient-dev python-dev libmariadbclient-dev \
                          libsasl2-dev libldap2-dev net-tools tcpdump \
                          curl iproute2 libgtk2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install virtualenv
RUN virtualenv -ppython3 unicms.env
RUN . unicms.env/bin/activate

# generate chosen locale
RUN sed -i 's/# it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen
RUN locale-gen it_IT.UTF-8
# set system-wide locale settings
ENV LANG it_IT.UTF-8
ENV LANGUAGE it_IT
ENV LC_ALL it_IT.UTF-8

COPY . /unicms
WORKDIR /unicms
RUN pip3 install -r requirements.txt

# Unical packages
RUN pip3 install git+https://github.com/UniversitaDellaCalabria/unicms-template-unical.git
# RUN pip3 install git+https://github.com/UniversitaDellaCalabria/unicms-editorial-board.git
# RUN pip3 install git+https://github.com/UniversitaDellaCalabria/unicms-calendar.git
# RUN pip3 install git+https://github.com/UniversitaDellaCalabria/unicms-unical-storage-handler.git

# settingslocal from example
RUN cp example/unicms/settingslocal_example.py example/unicms/settingslocal.py

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.2/wait /wait
RUN chmod +x /wait

# check with
# docker inspect --format='{{json .State.Health}}' uniticket
# HEALTHCHECK --interval=3s --timeout=2s --retries=1 CMD curl --fail http://localhost:8000/ || exit 1

RUN python3 example/manage.py migrate
# ADMIN as USERNAME, ADMINPASS as PASSWORD
RUN python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.filter(username='admin').exists() or get_user_model().objects.create_superuser('admin', 'admin@example.com', 'adminpass')"

RUN python3 example/manage.py unicms_collect_templates -y

# uncomment the following line to fill the database with the default users
# RUN python manage.py loaddata dumps/example_conf.json

EXPOSE 8000
CMD /wait && python example/manage.py runserver 0.0.0.0:8000
