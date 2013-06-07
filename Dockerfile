FROM base

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y -q python-virtualenv
RUN virtualenv /opt/wwc/edx

CMD /opt/wwc/edx/django-admin.py runserver --pythonpath=/opt/wwc/edx-platform --settings=lms.envs.dev
