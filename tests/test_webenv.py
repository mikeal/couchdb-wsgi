#!/usr/bin/python
import couchdb_wsgi
from webenv import Response
from webenv.rest import RestApplication

class ApplicationOne(RestApplication):
    pass

class ApplicationTwo(RestApplication):
    def GET(self, request, collection=None):
        return Response(str(collection))
        
application = ApplicationOne()
application.add_resource('two', ApplicationTwo())

couchdb_wsgi.CouchDBWSGIHandler(application).run()
