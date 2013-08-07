from google.appengine.api import memcache
from hashlib import md5
import urllib2
import StringIO
import httplib
import logging

class GMemcache(urllib2.BaseHandler):
    def __init__(self, maxAge = 21600):
        self.maxAge = maxAge
    
    def default_open(self, request):
        """Handles GET requests, if the response is cached it returns it
        """
        if request.get_method() is not "GET":
            return None # let the next handler try to handle the request

        thumb = md5(request.get_full_url()).hexdigest()
        header = thumb + ".headers"
        body = thumb + ".body"
        headerdata = memcache.get(header)
        bodydata = memcache.get(body)
        if (headerdata is not None) & (bodydata is not None):
            logging.info("Memcache hit")
            return CachedResponse(
                headerdata,
                bodydata,
                request.get_full_url(),
                "memcache"
            )
        else:
            return None  # let the next handler handle

    def http_response(self, request, response):
        """Gets a HTTP response, if it was a GET request and the status code
        starts with 2 (200 OK etc) it caches it and returns a CachedResponse
        """
        if (request.get_method() == "GET"
            and str(response.code).startswith("2")
        ):
            responseText = response.read()
            if 'x-memcache-cache' not in response.info():
                thumb = md5(request.get_full_url()).hexdigest()
                header = thumb + ".headers"
                body = thumb + ".body"
                logging.info("Memcache write")
                memcache.add(header, str(response.info()), self.maxAge)
                memcache.add(body, responseText, self.maxAge)
            return CachedResponse(
                str(response.info()),
                responseText,
                request.get_full_url(),
                ""
            )
        else:
            return response
        
class CachedResponse(StringIO.StringIO):
    """An urllib2.response-like object for cached responses.

    To determine if a response is cached or coming directly from
    the network, check the x-local-cache header rather than the object type.
    """

    #@locked_function
    def __init__(self, headerdata, bodydata, url, cache_header=""):
        StringIO.StringIO.__init__(self, bodydata)

        self.url     = url
        self.code    = 200
        self.msg     = "OK"
        headerbuf = headerdata
        if cache_header != "":
            headerbuf += "x-%s-cache: true\r\n" % (cache_header)
        self.headers = httplib.HTTPMessage(StringIO.StringIO(headerbuf))

    def info(self):
        """Returns headers
        """
        return self.headers

    def geturl(self):
        """Returns original URL
        """
        return self.url