'use strict';

angular.module('tvcalAppServices', ['ngResource']).
factory('Series', function($resource){
	return $resource('/search/:search');
});