import tvdb_api, tvdb_ui
import datetime
from icalendar import Calendar, Event
import urllib2
from GMemcache import GMemcache
import webapp2
import json

class Tvcal(webapp2.RequestHandler):
    def get(self, sids):
        self.response.headers['Content-Type'] = 'text/calendar'
        self.response.out.write(self.getCalendar(sids.split(',')))
        
    def getCalendar(self, sids):
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(GMemcache), apikey='DCDC02D859CD26EF')
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

allSeries = []

class List(tvdb_ui.BaseUI):
    # we want the list of all possibles, the result does not matter
    def selectSeries(self, series):
        # TODO: A bad hack and sure not threadsafe :(
        global allSeries
        allSeries = series;
        return series[0]   
        

class Search(webapp2.RequestHandler):
    def get(self, search):
        self.response.headers['Content-Type'] = 'application/json'
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(GMemcache), custom_ui=List)
        tvdb[search]      
        self.response.out.write(json.dumps(allSeries))
    
        
app = webapp2.WSGIApplication([('/tvdb-ical/([\d,]+)', Tvcal), 
                               ('/tvdb-ical/([\d,]+).ics', Tvcal),
                               ('/search/(.*)', Search)],
                              debug=True)