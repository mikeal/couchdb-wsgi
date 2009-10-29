#!/usr/bin/python
import couchdb_wsgi

import json
from StringIO import StringIO

import sys
def application(environ, start_response):
    start_response('200 Ok', [('content-type','text/plain',)])
    return 'Testing'

couchdb_wsgi.CouchDBWSGIHandler(application).run()
