/* global SortedSet */
'use strict';

angular.module('tvcalApp')
.controller('MainCtrl', function ($scope, Series) {
	$scope.submitSeach = function () {
		$scope.searchResult = Series.query({search: $scope.search});
	};
	$scope.selectedSeriesIds = new SortedSet();
	$scope.addSerie = function (id) {
		$scope.selectedSeriesIds.insert(id);
	};
	$scope.removeSerie = function (id) {
		$scope.selectedSeriesIds.remove(id);
	};
	$scope.isCollapsed = true;
	$scope.serverName = window.location.protocol + '//' + window.location.host;
});