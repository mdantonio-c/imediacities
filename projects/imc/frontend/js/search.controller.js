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
					self.numPerPage = 5; /*number of creations per page*/
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
				if (isNaN(secs)) {
					return "n/a";
				}
				var cdate = new Date(0, 0, 0, 0, 0, secs);
				if ((cdate.getHours() === 0) && (cdate.getMinutes() > 0)) {
					return cdate.getMinutes() + " min " + cdate.getSeconds() + " sec";
				} else if ((cdate.getHours() === 0) && (cdate.getMinutes() === 0)) {
					return cdate.getSeconds() + " sec";
				} else {
					return cdate.getHours() + " hour " + cdate.getMinutes() + " min " + cdate.getSeconds() + " sec";
				}
			};
		})
		// Filter a list of contributors by a given role
		.filter('contributorsByRole', function() {
			return function(inputArray, role) {
				if (!angular.isDefined(role) || role === '') {
					return inputArray;
				}
				var data = _.filter(inputArray, function(item) {
					if (!item.attributes.activities || !item.attributes.activities.length) {
						return false;
					}

					var isMatch = false;
					item.attributes.activities.forEach(function(r) {
						if (_.isObject(r)) {
							if (r.value === role) {
								isMatch = true;
							}
						} else {
							if (r === role) {
								isMatch = true;
							}
						}
					});

					return isMatch;
				});
				return data;
			};
		})
		.filter('nocomma', function() {
			return function(value) {
				return (!value) ? '' : value.replace(/,/g, '');
			};
		})
		.filter('currentYear', ['$filter', function($filter) {
			return function() {
				return $filter('date')(new Date(), 'yyyy');
			};
		}])
		;

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
		$scope.resetPager = function() {
			self.currentPage = 1;
			self.ItemsByPage = self.typeOptions[0].value;
		};
		$scope.resetPager();
		self.maxSize = 5;
		self.totalItems = 0;

		self.creations = [];

		self.loading = false;
		self.inputTerm = "";
		self.inputProvider = "";
		self.inputItemType = "all";
		self.advancedSearch = false;

		// list of match field
		self.matchFields = ["title", "keyword", "description", "contributor"];
		// Selected fields
		self.selectedMatchFields = ["title"];
		// Toggle selection for a given field by name
		self.toggleMatchFieldSelection = function(matchField) {
			var idx = self.selectedMatchFields.indexOf(matchField);
			// Is currently selected
			if (idx > -1) {
				self.selectedMatchFields.splice(idx, 1);
			}
			// Is newly selected
			else {
				self.selectedMatchFields.push(matchField);
			}
		};

		self.searchCreations = function() {
			var request_data = {};
			if (self.advancedSearch) {
				request_data = {
					"match": {
						"term": "",
						"fields": self.selectedMatchFields,
					},
					"filter": {
						"type": self.inputItemType,
						"provider": self.inputProvider,
						"country": self.inputCountry,
						"iprstatus": self.inputIPRStatus,
						"yearfrom": $scope.search.year_min.toString(),
						"yearto": $scope.search.year_max.toString(),
					}
				};
			} else {
				request_data = {
					"match": {
						"term": "",
						"fields": ["title"],
					},
				};
			}
			request_data.match.term = self.inputTerm === '' ? '*' : self.inputTerm;
			self.loadResults = false;
			self.loading = true;
			self.showmese = true;
			DataService.searchCreations(request_data, self.currentPage, self.ItemsByPage).then(
				function(out_data) {
					var meta = out_data.data.Meta;
					self.totalItems = meta.totalItems;
					self.creations = out_data.data.Response.data;
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
					self.showmese = false;
					noty.extractErrors(out_data, noty.ERROR);
				});
		};

		self.resetAndSearch = function() {
			$scope.resetPager();
			self.searchCreations();
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
			self.searchCreations();
		}

		$scope.setPage = function() {
			self.currentPage = this.n;
			self.searchCreations();
		};

		$scope.firstPage = function() {
			self.currentPage = 1;
			self.searchCreations();
		};

		$scope.lastPage = function() {
			self.currentPage = parseInt(self.totalItems / self.ItemsByPage) + 1;
			self.searchCreations();
		};

		$scope.setItemsPerPage = function(num) {
			self.itemsPerPage = num;
			self.currentPage = 1; //reset to first page
			self.searchCreations();
		};

		$scope.pageChanged = function() {
			//console.log('Page changed to: ' + self.currentPage);
			self.searchCreations();
		};

		$scope.range = function(input, total) {
			var ret = [];
			if (!total) {
				total = input;
				input = 0;
			}
			for (var i = input; i < total; i++) {
				if (i !== 0 && i !== total - 1) {
					ret.push(i);
				}
			}
			return ret;
		};

		// advanced search
		self.toggleAdvancedSearch = function() {
			if ($scope.asCollapsed) {
				self.advancedSearch = false;
			} else {
				self.advancedSearch = true;
			}
		};

		$scope.asCollapsed = true;
		$scope.providers = [{
			"code": "CCB",
			"name": "CCB - Cineteca di Bologna"
		}, {
			"code": "CRB",
			"name": "CRB - Cinematheque Royale de Belgique"
		}, {
			"code": "DFI",
			"name": "DFI - Det Danske Filminstitut"
		}, {
			"code": "DIF",
			"name": "DIF - Deutsches Filminstitut"
		}, {
			"code": "FDC",
			"name": "FDC - Filmoteca de Catalunya"
		}, {
			"code": "MNC",
			"name": "MNC - Museo Nazionale del Cinema"
		}, {
			"code": "OFM",
			"name": "OFM - Österreichisches Filmmuseum"
		}, {
			"code": "SFI",
			"name": "SFI - Svenska Filminstitutet"
		}, {
			"code": "TTE",
			"name": "TTE - Greek Film Archive"
		}];
		self.inputItemType = "all";
		$scope.cleanupFilters = function() {
			self.inputItemType = "all";
			self.inputProvider = "";
		};

		// move codelist provision in a service
		self.iprstatuses = [{
			"code": "01",
			"name": "In copyright"
		}, {
			"code": "02",
			"name": "EU Orphan Work"
		}, {
			"code": "03",
			"name": "In copyright - Educational use permitted"
		}, {
			"code": "04",
			"name": "In copyright - Non-commercial use permitted"
		}, {
			"code": "05",
			"name": "Public Domain"
		}, {
			"code": "06",
			"name": "No Copyright - Contractual Restrictions"
		}, {
			"code": "07",
			"name": "No Copyright - Non-Commercial Use Only"
		}, {
			"code": "08",
			"name": "No Copyright - Non-Commercial Use Only"
		}, {
			"code": "09",
			"name": "No Copyright - United States"
		}, {
			"code": "10",
			"name": "Copyright Undetermined"
		}];

		self.countries = [{
			"code": "IT",
			"name": "Italy"
		}, {
			"code": "AT",
			"name": "Austria"
		}, {
			"code": "BE",
			"name": "Belgium"
		}, {
			"code": "DE",
			"name": "Germany"
		}, {
			"code": "ES",
			"name": "Spain"
		}, {
			"code": "FI",
			"name": "Finland"
		}, {
			"code": "FR",
			"name": "France"
		}, {
			"code": "GB",
			"name": "United Kingdom"
		}, {
			"code": "GR",
			"name": "Greece"
		}];
	}

})();