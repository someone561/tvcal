'use strict';

describe('Filter: tvdbbanner', function () {

  // load the filter's module
  beforeEach(module('tvcalApp'));

  // initialize a new instance of the filter before each test
  var tvdbbanner;
  beforeEach(inject(function ($filter) {
    tvdbbanner = $filter('tvdbbanner');
  }));

  it('should return the input prefixed with "/tvdbimages/"', function () {
    var text = 'angularjs.png';
    expect(tvdbbanner(text)).toBe('/tvdbimages/' + text);
  });
  
  it('should be empty if null, undefined, or empty goes in', function () {
	expect(tvdbbanner('')).toBe('');
	expect(tvdbbanner(undefined)).toBe('');
	expect(tvdbbanner(null)).toBe('');
  });

});
