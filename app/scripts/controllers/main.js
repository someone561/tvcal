/* global SortedSet, $ */
'use strict';

angular.module('tvcalApp')
.controller('MainCtrl', function ($scope, Series) {
	$scope.searching = false;
	$scope.submitSeach = function () {
		$scope.searching = true;
		$('#errorMessage').removeClass('in');
		$scope.empty = false;
		$scope.searchQuery = $scope.search;
		$scope.searchResult = Series.query({search: $scope.search},
		function () {
			$scope.searching = false;
			$scope.empty = $scope.searchResult.length === 0;
		}, function (response) {
			$scope.searching = false;
			$('#errorMessage').addClass('in');
			$scope.errorText = response.data + '. Statuscode was ' + response.status;
		});
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