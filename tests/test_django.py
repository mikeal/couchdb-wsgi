#!/usr/bin/python
import os, sys
import couchdb_wsgi

django_project = os.path.join(os.path.dirname(__file__), 'django_test')
sys.path.append(django_project)
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_test.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

couchdb_wsgi.CouchDBWSGIHandler(application).run()

