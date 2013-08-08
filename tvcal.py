import tvdb_api
import datetime
from icalendar import Calendar, Event
import urllib2
from GMemcache import GMemcache
import webapp2
import json
from DatastoreCache import DataStoreCache
from google.appengine.ext import db

apikey='DCDC02D859CD26EF'

class Tvcal(webapp2.RequestHandler):
    def get(self, sids):
        self.response.headers['Content-Type'] = 'text/calendar'
        self.response.out.write(self.getCalendar(sids.split(',')))
        
    def getCalendar(self, sids):
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(GMemcache, DataStoreCache), apikey=apikey)
        cal = Calendar()
        cal.add('prodid', '-//tvcal//mxm.dk//')
        cal.add('version', '2.0')    
    
        for sid in sids:
            serie = tvdb[int(sid)]
            [cal.add_component(self.createEvent(episode, serie['seriesname'])) for season in serie.values() 
                for episode in season.values() 
                    if episode['firstaired']]
        return cal.to_ical()
    
    def createEvent(self, episode, serie):
        event = Event()
        event.add('uid', episode["id"])
        event.add('summary', '%s S%02dE%02d %s' % (serie, int(episode['seasonnumber']), int(episode['episodenumber']), episode['episodename']))
        event.add('dtend', datetime.datetime.strptime(episode['firstaired'], "%Y-%m-%d").date())
        event.add('dtstart', datetime.datetime.strptime(episode['firstaired'], "%Y-%m-%d").date())
        return event

class Search(webapp2.RequestHandler):
    def get(self, search):
        self.response.headers['Content-Type'] = 'application/json'
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(GMemcache, DataStoreCache), apikey=apikey)
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