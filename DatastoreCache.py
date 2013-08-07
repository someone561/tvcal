from google.appengine.ext import db
from hashlib import md5
import urllib2
from GMemcache import CachedResponse
import logging
import datetime


class HttpCache(db.Model):
    header = db.TextProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(required=True)

class DataStoreCache(urllib2.BaseHandler):
    def __init__(self, maxAge = 21600):
        self.maxAge = maxAge
    
    def default_open(self, request):
        """Handles GET requests, if the response is cached it returns it
        """
        if request.get_method() is not "GET":
            return None # let the next handler try to handle the request

        thumb = md5(request.get_full_url()).hexdigest()
        cache = HttpCache.get_by_key_name(thumb)
        #cache = db.GqlQuery("SELECT * FROM HttpCache WHERE __key__ = :1", thumb).get()
        if (cache is not None):
            logging.info("Datastore Cache hit")
            if (datetime.datetime.now() - cache.created > datetime.timedelta(seconds=self.maxAge)):
                logging.info("But Cache is to old")
                cache.delete()
                return None
            return CachedResponse(
                cache.header,
                cache.body.encode('utf-8'),
                request.get_full_url(),
                "datastore"
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
            # We assume that a result come from memcache is already in datastore
            if ('x-datastore-cache' not in response.info()
                and 'x-memcache-cache' not in response.info()):
                # Response is not cached
                set_cache_header = "datastore"               
                thumb = md5(request.get_full_url()).hexdigest()                                      
                cache = HttpCache(key_name=thumb,
                                  header=str(response.info()),
                                  body=unicode(responseText.decode('utf-8')),
                                  created=datetime.datetime.now())
                logging.info("Datastore Cache write")
                cache.put();
            else:
                set_cache_header = ""
            return CachedResponse(
                str(response.info()),
                responseText,
                request.get_full_url(),
                set_cache_header
            )
        else:
            return response