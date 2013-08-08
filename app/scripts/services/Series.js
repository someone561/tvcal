'use strict';

angular.module('tvcalApp')
  .factory('Series', function ($resource) {
    return $resource('/search/:search');
  });
