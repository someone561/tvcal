import tvdb_api, tvdb_ui
import datetime
from icalendar import Calendar, Event
import urllib2
import logging
from GMemcache import GMemcache
import webapp2
import json

sids = ['The Big Bang Theory', 'NCIS', 'Mad Men', 'Futurama', 'Game of Thrones', 'Breaking Bad', 'The Simpsons']


"""if __name__ == "__main__":
    print 'Content-Type: text/plain'
    print ''
    print getCalendar(sids)
    """

class Tvcal(webapp2.RequestHandler):
    def get(self, sids):
        self.response.headers['Content-Type'] = 'text/plain' #'text/calendar'
        self.response.out.write(self.getCalendar(sids.split(',')))
        
    def getCalendar(self, sids):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        #tvdb = tvdb_api.Tvdb(apikey="0BB856A59C51D607")
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(GMemcache))
        #logging.debug(tvdb['NCIS'])
        #return tvdb['NCIS']
        cal = Calendar()
        cal.add('prodid', '-//tvcal//mxm.dk//')
        cal.add('version', '2.0')
    
    
        for sid in sids:
            serie = tvdb[int(sid)]
            [cal.add_component(self.createEvent(episode, sid)) for season in serie.values() 
                for episode in season.values() 
                    if episode['firstaired'] and datetime.datetime.strptime(episode['firstaired'], "%Y-%m-%d").date() >= (datetime.date.today()-datetime.timedelta(weeks=2))]
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
        # TODO JSON
        self.response.headers['Content-Type'] = 'text/plain'
        tvdb = tvdb_api.Tvdb(cache=urllib2.build_opener(GMemcache), custom_ui=List)
        tvdb[search]      
        self.response.out.write(json.dumps(allSeries))
    
        
app = webapp2.WSGIApplication([('/tvcal/([\d,]+)', Tvcal), 
                               ('/tvcal/([\d,]+).ics', Tvcal),
                               ('/search/(.*)', Search)],
                              debug=True)