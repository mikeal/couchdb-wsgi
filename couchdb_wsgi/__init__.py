import sys
import traceback
from StringIO import StringIO

try:
    # Python 2.6
    import json
except:
    # Prior to 2.6 requires simplejson
    import simplejson as json
    
import urlencoding    

"""
{
    'body': 'undefined',
    'cookie': {
        '__utma': '96992031.3087658685658095000.1224404084.1226129950.1226169567.5',
        '__utmz': '96992031.1224404084.1.1.utmcsr'
    },
    'form': {},
    'info': {
        'compact_running': False,
        'db_name': 'couchbox',
        'disk_size': 50559251,
        'doc_count': 9706,
        'doc_del_count': 0,
        'purge_seq': 0,
        'update_seq': 9706},
    'path': [],
    'query': {},
    'verb': 'GET'
}
"""

class CouchDBWSGIHandler(object):
    def __init__(self, request):
        self.request = request
        self.start_response_called = False
        
    @property
    def environ(self):
        environ = {}
        cdict = self.request
        ###--- CouchDB variables ---###
        environ['couchdb.request'] = cdict
        environ['couchdb.info'] = cdict['info']
        
        ###--- Environ variables from CGI ---###
        if cdict['body'] == 'undefined':
            cdict['body'] = ''
        environ = {}
        environ['REQUEST_METHOD'] = cdict['verb']
        environ['CONTENT_LENGTH'] = len(cdict['body'])
        
        for header, value in cdict['headers'].items():
            environ['HTTP_'+header.upper().replace('-','_')] = value
            
        # Reconstruct the path and script    
        script, path = cdict['path'][:2], cdict['path'][2:]
        if len(path) is not 0:
            path = '/' + '/'.join(path) 
        else: path = ''
        script = '/' + '/'.join(script)
        
        if cdict['query']:
            environ['QUERY_STRING'] = urlencoding.compose_qs(cdict['query'])        
        
        # Unclear whether this works with port 80
        environ['SERVER_NAME'], environ['SERVER_PORT'] = environ['HTTP_HOST'].split(':')
        environ['SERVER_PORT'] = int(environ['SERVER_PORT'])
        # Faking, version isn't specified yet
        environ['HTTP_VERSION'] = 'HTTP/1.1'
        
        ###--- WSGI specific variables --##
        environ['wsgi.version'] = (1,0)
        environ['wsgi.input'] = StringIO(cdict['body'])
        # Faking, scheme isn't currently available
        environ['wsgi.url_scheme'] = 'http'
        environ['wsgi.errors'] = StringIO()
        # Not actually sure about these ones :)
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = True
        
        return environ
    
    def start_response(self, status, response_headers, exc_info=None):
        self.code = int(status.split(' ')[0])
        self.headers = dict(response_headers)
        self.start_response_called = True

class CouchDBWSGIParser(object):
    def __init__(self, application):
        self.application = application
        
    def requests(self):
        line = sys.stdin.readline()
        while line:
            yield json.loads(line)
            line = sys.stdin.readline()
    
    def handle_request(self, request):
        r = CouchDBWSGIHandler(request)
        try:
            response = self.application(r.environ, r.start_response)
        except:
            r.status = 500
            response = traceback.format_exc()
            r.headers = {'content-type':'text/plain'}
            
        sys.stdout.write(json.dumps({'code':r.code, 'body':response, 'headers':r.headers})+'\n')
        sys.stdout.flush()
    
    def run(self):
        for req in self.requests():
            self.handle_request(req)
