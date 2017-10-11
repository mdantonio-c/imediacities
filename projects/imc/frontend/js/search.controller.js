(function() {
	'use strict';

	var app = angular.module('web')
		.controller('SearchController', SearchController);

	// create a simple search filter
	app.filter('searchFor', function() {
			return function(arr, searchString, $scope) {
				if (searchString === '*') {
					return arr;
				} else if (searchString) {

					var result = [];

					searchString = searchString.toLowerCase();

					angular.forEach(arr, function(item) {
						if (item.attributes.identifying_title.toLowerCase().indexOf(searchString) !== -1) {
							result.push(item);
						}
					});

					/*pagination*/
					self.numPerPage = 5; /*number of videos per page*/
					$scope.noOfPages = Math.ceil(result.length / self.numPerPage);
					$scope.currentPage = 1;
					/*---*/

					return result;
				}
			};
		})
		// convert float to integer
		.filter('parseNum', function() {
			return function(input) {
				var secs = parseInt(input, 10);
				var cdate = new Date(0, 0, 0, 0, 0, secs);
				if ((cdate.getHours() === 0) && (cdate.getMinutes() > 0)) {
					return cdate.getMinutes() + " mins " + cdate.getSeconds() + " secs";
				} else if ((cdate.getHours() === 0) && (cdate.getMinutes() === 0)) {
					return cdate.getSeconds() + " secs";
				} else {
					return cdate.getHours() + " hours " + cdate.getMinutes() + " mins " + cdate.getSeconds() + " secs";
				}
			};
		});
	
	// The controller
	function SearchController($scope, $log, $document, $state, $stateParams, DataService, noty, $uibModal) {
		var self = this;

		self.showmesb = false;
		self.viewlogo = true;
		self.showmese = false;
		//self.showmepg = true;

		/*Define options type for paginate page numbers*/
		self.typeOptions = [{
			name: '4 per page',
			value: '4'
		}, {
			name: '8 per page',
			value: '8'
		}, {
			name: '15 per page',
			value: '15'
		}, {
			name: '20 per page',
			value: '20'
		}];

		//configure pagination
		self.ItemsByPage = self.typeOptions[0].value;
		self.maxSize = 5;
		self.currentPage = 1;
		self.numvideos = 0;

		self.totalItems = 0;

		self.videos = [];

		self.loading = false;
		self.inputTerm = "";
		self.searchVideos = function() {
			var request_data = {
				"type": "video",
				"term": ""
			};
			request_data.term = self.inputTerm === '' ? '*' : self.inputTerm;
			/*request_data.numpage = self.currentPage;
			request_data.pageblock = self.ItemsByPage;*/
			// console.log('search videos with term: ' + request_data.term);
			self.loadResults = false;
			self.loading = true;
			self.showmese = true;
			DataService.searchVideos(request_data, self.currentPage, self.ItemsByPage).then(
				function(out_data) {
					self.numvideos = parseInt(out_data.data[out_data.data.length - 1]);
					self.totalItems = self.numvideos;
					out_data.data.pop();
					self.videos = out_data.data;
					self.loading = false;
					self.loadResults = true;
					self.showmese = false;
					// Calculate Total Number of Pages based on Search Result
					noty.extractErrors(out_data, noty.WARNING);
				},
				function(out_data) {
					self.loading = false;
					self.studyCount = 0;
					self.loadResults = true;
					noty.extractErrors(out_data, noty.ERROR);
				});
		};

		self.goToSearch = function(event, term) {
			if (event.keyCode === 13) {
				$state.go('logged.search', {
					q: term
				});
			}
		};

		var term = $stateParams.q;
		if (term !== undefined && term !== '') {
			self.viewlogo = false;
			self.inputTerm = term;
			self.searchVideos();
		}

		$scope.setPage = function() {
			self.currentPage = this.n;
			self.searchVideos();
		};

		$scope.firstPage = function() {
			self.currentPage = 1;
			self.searchVideos();
		};

		$scope.lastPage = function() {
			self.currentPage = parseInt(self.numvideos / self.ItemsByPage) + 1;
			self.searchVideos();
		};

		$scope.setItemsPerPage = function(num) {
			self.itemsPerPage = num;
			self.currentPage = 1; //reset to first page
			self.searchVideos();
		};

		$scope.pageChanged = function() {
			//console.log('Page changed to: ' + self.currentPage);
			self.searchVideos();
		};


		$scope.range = function(input, total) {
			var ret = [];
			if (!total) {
				total = input;
				input = 0;
			}
			for (var i = input; i < total; i++) {
				if (i !== 0 && i !== total-1) {
					ret.push(i);
				}
			}
			return ret;
		};
	}

})();