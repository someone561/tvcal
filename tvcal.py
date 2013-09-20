import tvdb_api
import datetime
from icalendar import Calendar, Event
import urllib2
import webapp2
import json
import logging
from DatastoreCache import DataStoreCache
from google.appengine.ext import db

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
        cache = CalendarEntry(key_name=serie['id'],
                      created=datetime.datetime.now())
        for season in serie.values():
            for episode in season.values():
                if (episode['firstaired']):
                    cache.summaries.append('%s S%02dE%02d %s' % (serie['seriesname'], int(episode['seasonnumber']), int(episode['episodenumber']), episode['episodename']))
                    cache.dates.append(episode['firstaired'])
                    cache.uids.append(episode['id'])
        return cache
    
    def getCache(self, tvdb, sid):
        cache = CalendarEntry.get_by_key_name(sid)
        if (cache is not None):
            logging.info("Datastore Cache hit")
            if (datetime.datetime.now() - cache.created < datetime.timedelta(seconds=self.maxAge)):
                return cache
            logging.info("But Cache is to old")
            cache.delete()
        logging.info("Query tvdb")
        cache = self.createCalendarEntry(tvdb[int(sid)])
        cache.put()
        return cache
        
    def getDetails(self, episode, serie):
        return ('%s S%02dE%02d %s' % (serie, int(episode['seasonnumber']), int(episode['episodenumber']), episode['episodename']), episode['firstaired']) 

class Search(webapp2.RequestHandler):
    def get(self, search):
        self.response.headers['Content-Type'] = 'application/json'
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(DataStoreCache), apikey=apikey)
        self.response.out.write(json.dumps(tvdb.search(search)))

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