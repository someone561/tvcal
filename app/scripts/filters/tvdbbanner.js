'use strict';

angular.module('tvcalApp')
  .filter('tvdbbanner', function () {
    return function (input) {
      return input ? '/banners/' + input : '';
    };
  });
