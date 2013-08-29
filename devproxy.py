import webapp2
import urllib2

# A very simple Proxy (actual only for get request)
class Proxy(webapp2.RequestHandler):
    def get(self):
        headers = {}
        for i,v in self.request.headers.items():
            headers[i] = v
        try:
            resquest = urllib2.Request('http://localhost:9000/' + self.request.path_qs.split('#', 1)[0], headers=headers)
            res = urllib2.urlopen(resquest)
        except urllib2.HTTPError as e:
            # If we got a other status code then 200, set then and resume
            self.response.status = e.code 
            res = e
        for i,v in res.info().items():
            self.response.headers[i] = v;
        self.response.out.write(res.read())


app = webapp2.WSGIApplication([('/.*', Proxy)],
                              debug=True)