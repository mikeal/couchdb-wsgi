import sys

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

class CouchDBWSGIParser(object):
    def __init__(self, application):
        pass

    def couch_to_environ(self, cdict):
        if cdict['body'] == 'undefined':
            cdict['body'] = ''
        environ = {}
        environ['REQUEST_METHOD'] = cdict['verb']
        environ['COUCHDB_INFO'] = cdict['info']
        for header, value in cdict['headers'].items():
            environ['HTTP_'+header.upper().replace('-','_')] = value
        # Reconstruct the path    
        path = '/'.join(cdict['path'])    
        if cdict['query']:
            qs = urlencoding.compose_qs(cdict['query'])
            path + '?' + qs
        
        
        
    def process_line(self, line):
        cdict = json.loads(line)    
        
        environ = couch_to_environ(cdict)
        return environ
        
    def run(self):
        pass

def requests():
    # 'for line in sys.stdin' won't work here
    line = sys.stdin.readline()
    while line:
        yield json.loads(line)
        line = sys.stdin.readline()

def respond(code=200, data={}, headers={}):
    sys.stdout.write("%s\n" % json.dumps({"code": code, "json": data, "headers": headers}))
    sys.stdout.flush()

def main():
    for req in requests():
        respond(data={"qs": req["query"]})

if __name__ == "__main__":
    main()