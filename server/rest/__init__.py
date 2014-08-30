"""
Simple methods to interact with REST resources.
Mainly to avoid messing too much with urllib2 all over the place.

Under normal circumstances, this would have been done through the requests module,
but since that's not builtin we'll just go with urllib.
"""
import urllib2
import json
from lxml import objectify

def get(url):
    return __execute(url, 'GET')

def put(url, data):
    return __execute(url, "PUT", data)

def head(url):
    return __execute(url, "HEAD")

def post(url, data):
    return __execute(url, "POST", data)

def __execute(url, method, data = None):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    if data:
        body = json.dumps(data)
    else:
        body = None
    req = urllib2.Request(url, data=body)
    req.add_header("Accept", "application/json; text/xml")
    if data:
        req.add_header("Content-Type", "application/json")

    req.get_method = lambda: method
    f = opener.open(req)
    if f and f.info().getheader("Content-Length") != "0":
        if f.info().getheader("Content-Type").startswith("application/json"):
            return json.load(f)
        elif f.info().getheader("Content-Type").startswith("text/xml"):
            str = f.read()
            body = objectify.fromstring(str)
            return body
    else:
        return None
