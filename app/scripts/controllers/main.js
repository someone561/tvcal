/* global SortedSet, $ */
'use strict';

angular.module('tvcalApp')
.controller('MainCtrl', function ($scope, Series) {
	$scope.submitSeach = function () {
		$scope.searchResult = Series.query({search: $scope.search},
		function () {
			// do nothing additional on success
		}, function (response) {
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