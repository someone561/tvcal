.PHONY: all clean run
pytz-version=2013b
dateutil-version=2.1
icalendar-version=3.5
six-version=1.3.0
tbdb_api-version=8441558b6758f6d79fff0691f6b2a77d3d06fd99

all: pytz dateutil icalendar six.py tvdb_api.py tvdb_cache.py tvdb_exceptions.py tvdb_ui.py node_modules app/bower_components dist 

clean:
	rm -rf pytz dateutil icalendar six.py tvdb_api.py tvdb_cache.py tvdb_exceptions.py tvdb_ui.py *.pyc

pytz:
	wget https://pypi.python.org/packages/source/p/pytz/pytz-$(pytz-version).tar.gz --quiet -O - | tar xvz
	mv pytz-$(pytz-version)/pytz .
	rm -r pytz-$(pytz-version)
	
dateutil:
	wget https://pypi.python.org/packages/source/p/python-dateutil/python-dateutil-$(dateutil-version).tar.gz --quiet -O - | tar xvz
	mv python-dateutil-$(dateutil-version)/dateutil .
	rm -r python-dateutil-$(dateutil-version)
	
icalendar:
	wget https://pypi.python.org/packages/source/i/icalendar/icalendar-$(icalendar-version).tar.gz --quiet -O - | tar xvz
	mv icalendar-$(icalendar-version)/src/icalendar .
	rm -r icalendar-$(icalendar-version)

six.py:
	wget https://pypi.python.org/packages/source/s/six/six-$(six-version).tar.gz --quiet -O - | tar xvz
	mv six-$(six-version)/six.py .
	rm -r six-$(six-version)
	
tvdb_api.py tvdb_cache.py tvdb_exceptions.py tvdb_ui.py:
	wget https://raw.github.com/dbr/tvdb_api/$(tbdb_api-version)/tvdb_api.py
	wget https://raw.github.com/dbr/tvdb_api/$(tbdb_api-version)/tvdb_cache.py
	wget https://raw.github.com/dbr/tvdb_api/$(tbdb_api-version)/tvdb_exceptions.py
	wget https://raw.github.com/dbr/tvdb_api/$(tbdb_api-version)/tvdb_ui.py
	#wget https://pypi.python.org/packages/source/t/tvdb_api/tvdb_api-$(tbdb_api-version).tar.gz --quiet -O - | tar xvz
	#mv tvdb_api-$(tbdb_api-version)/tvdb*.py .
	#rm -r tvdb_api-$(tbdb_api-version)
	
dist: app
	grunt

node_modules:
	npm install

app/bower_components:
	bower install

run: all
	$(GOOGLE_APP_ENGINE)/dev_appserver.py .