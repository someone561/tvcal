import tvdb_api
import datetime
from icalendar import Calendar, Event
import urllib2
import webapp2
import json
import logging
from DatastoreCache import DataStoreCache
from google.appengine.ext import db
from google.appengine.api import memcache

apikey='DCDC02D859CD26EF'

class CalendarEntry(db.Model):
    # Three List to simulate a list of trippel
    summaries = db.StringListProperty()
    dates = db.StringListProperty()
    uids = db.StringListProperty()
    created = db.DateTimeProperty(required=True)

class Tvcal(webapp2.RequestHandler):
    maxAge = 21600
    
    def get(self, sids):
        self.response.headers['Content-Type'] = 'text/calendar'
        self.response.out.write(self.getCalendar(sids.split(',')))
        
    def getCalendar(self, sids):
        # Caching is done on applikation layer
        tvdb = tvdb_api.Tvdb(cache=False, apikey=apikey)
        cal = Calendar()
        cal.add('prodid', '-//tvcal//mxm.dk//')
        cal.add('version', '2.0')    
        
        entries = [self.getCache(tvdb, sid) for sid in sids]
        for e in entries:
            [cal.add_component(self.createEvent(*details)) for details in zip(e.uids, e.summaries, e.dates)]
        return cal.to_ical()
    
    def createEvent(self, uid, summary, date):
        event = Event()
        event.add('uid', uid)
        event.add('summary', summary)
        dateString = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        event.add('dtend', dateString)
        event.add('dtstart', dateString)
        return event
        
    def createCalendarEntry(self, serie):
        summaries = []
        dates = []
        uids = []
        for season in serie.values():
            for episode in season.values():
                if (episode['firstaired']):
                    summaries.append('%s S%02dE%02d %s' % (serie['seriesname'], int(episode['seasonnumber']), int(episode['episodenumber']), episode['episodename']))
                    dates.append(episode['firstaired'])
                    uids.append(episode['id'])
        cache = CalendarEntry(key_name=serie['id'],
            summaries=summaries,
            dates=dates,
            uids=uids,
            created=datetime.datetime.now())
        return cache
    
    def getCache(self, tvdb, sid):
        cache = memcache.get(sid)
        if cache is not None:
            logging.info("Memcache hit")
            return cache
        cache = CalendarEntry.get_by_key_name(sid)
        if (cache is not None):
            logging.info("Datastore Cache hit")
            if (datetime.datetime.now() - cache.created < datetime.timedelta(seconds=self.maxAge)):
                logging.info("write to memcache")
                memcache.add(sid, cache, self.maxAge)
                return cache
            logging.info("But Cache is to old")
            cache.delete()
        logging.info("Query tvdb")
        cache = self.createCalendarEntry(tvdb[int(sid)])
        cache.put()
        logging.info("write to memcache")
        memcache.add(sid, cache, self.maxAge)
        return cache
        
    def getDetails(self, episode, serie):
        return ('%s S%02dE%02d %s' % (serie, int(episode['seasonnumber']), int(episode['episodenumber']), episode['episodename']), episode['firstaired']) 

class SearchResult(db.Model):
    result = db.TextProperty()
    created = db.DateTimeProperty(required=True)

class Search(webapp2.RequestHandler):
    maxAge = 21600
    
    def get(self, search):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(self.getSearchResult(search))
        
    def getSearchResult(self, search):
        cache = memcache.get('Search_' + search)
        if cache is not None:
            logging.info("Memcache hit")
            return cache.result
        cache = SearchResult.get_by_key_name(search)
        if (cache is not None):
            logging.info("Datastore Cache hit")
            if (datetime.datetime.now() - cache.created < datetime.timedelta(seconds=self.maxAge)):
                logging.info("write to memcache")
                memcache.add('Search_' + search, cache, self.maxAge)
                return cache.result
            logging.info("But Cache is to old")
            cache.delete()
        logging.info("Query tvdb")
        # Caching is done on applikation layer
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(DataStoreCache), apikey=apikey)
        cache = SearchResult(key_name=search,
            result=json.dumps(tvdb.search(search)),
            created=datetime.datetime.now())
        cache.put()
        logging.info("write to memcache")
        memcache.add('Search_' + search, cache, self.maxAge)
        return cache.result

class Banner(db.Model):
    image = db.BlobProperty(required=True)
    created = db.DateTimeProperty()

class Graphical(webapp2.RequestHandler):
    def get(self, img):
        banner = Banner.get_by_key_name(img)
        if (banner is None):
            try:
                response = urllib2.urlopen("http://thetvdb.com/banners/graphical/%s?apikey=%s" % (img, apikey))
            except urllib2.HTTPError:
                self.error(404)
                return
            banner = Banner(key_name=img,
               image=response.read(),
               created=datetime.datetime.now())
            banner.put()
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(banner.image)
        
app = webapp2.WSGIApplication([('/tvdb-ical/([\d,]+)', Tvcal), 
                               ('/tvdb-ical/([\d,]+).ics', Tvcal),
                               ('/search/(.*)', Search),
                               ('/tvdbimages/graphical/(.*)', Graphical)],
                              debug=True)