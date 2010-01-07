#!/usr/bin/env python
import json
import uuid
import sys

if __name__ == "__main__":
    line = sys.stdin.readline()
    while line:
        u = str(uuid.uuid1())
        sys.stdout.write(json.dumps(['defer', u])+'\n')
        sys.stdout.flush()
        sys.stdout.write(json.dumps({'code':200,'body':'hello world', 'headers':{'Content-Type':'text/plain'},'session':u})+'\n')
        line = sys.stdin.readline()
