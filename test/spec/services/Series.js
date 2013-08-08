'use strict';

describe('Service: Series', function () {

  // load the service's module
  beforeEach(module('tvcalApp'));

  // instantiate service
  var Series;
  beforeEach(inject(function (_Series_) {
    Series = _Series_;
  }));

  it('should have a query method', function () {
    expect(Series.query);
  });

});
