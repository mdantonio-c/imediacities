(function() {
	'use strict';

	var providers = [{
			"code": "CCB",
			"name": "CCB - Cineteca di Bologna",
			"city": {
				// Bologna, Italy
				"position": [44.494887, 11.3426162],
				"name": "Bologna"
			}
		}, {
			"code": "CRB",
			"name": "CRB - Cinematheque Royale de Belgique",
			"city": {
				// Brussels, Belgium
				"position": [50.8503463, 4.3517211],
				"name": "Brussels"
			}
		}, {
			"code": "DFI",
			"name": "DFI - Det Danske Filminstitut",
			"city": {
				// Copenhagen, Denmark
				"position": [55.6760968, 12.568337199999974],
				"name": "Copenhagen"
			}
		}, {
			"code": "DIF",
			"name": "DIF - Deutsches Filminstitut",
			"city": {
				// Frankfurt am Main, German
				"position": [50.1109221, 8.682126700000026],
				"name": "Frankfurt am Main"
			}
		}, {
			"code": "FDC",
			"name": "FDC - Filmoteca de Catalunya",
			"city": {
				// Barcelona, Spain
				"position": [41.3850639, 2.1734034999999494],
				"name": "Barcelona"
			}
		}, {
			"code": "MNC",
			"name": "MNC - Museo Nazionale del Cinema",
			"city": {
				// Turin, Italy
				"position": [45.070312, 7.686856499999976],
				"name": "Turin"
			}
		}, {
			"code": "OFM",
			"name": "OFM - Österreichisches Filmmuseum",
			"city": {
				// Vienna, Austria
				"position": [48.2081743, 16.37381890000006],
				"name": "Vienna"
			}
		}, {
			"code": "SFI",
			"name": "SFI - Svenska Filminstitutet",
			"city": {
				// Stockholm, Sweden
				"position": [59.32932349999999, 18.068580800000063],
				"name": "Stockholm"
			}
		}, {
			"code": "TTE",
			"name": "TTE - Greek Film Archive",
			"city": {
				// Athens, Greece
				"position": [37.9838096, 23.727538800000048],
				"name": "Athens"
			}
		}];

	function getPosition(provider) {
		for (var i = 0; i < providers.length; i++) {
			if (providers[i].code === provider) {
				return providers[i].city.position;
			}
		}
	}

	var iprstatuses = [{
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
			"name": "No Copyright - Other Known Legal Restrictions"
		}, {
			"code": "09",
			"name": "No Copyright - United States"
		}, {
			"code": "10",
			"name": "Copyright Undetermined"
		}];

	var app = angular.module('web')
		.controller('SearchController', SearchController)
		.controller('NewSearchController', NewSearchController);

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
		.filter('providerToCity', function() {
			return function(provider) {
				if (provider === 'CCB') return 'Bologna';
				else if (provider === 'CRB') return 'Brussels';
				else if (provider === 'DFI') return 'Copenhagen';
				else if (provider === 'DIF') return 'Frankfurt am Main';
				else if (provider === 'FDC') return 'Barcelona';
				else if (provider === 'MNC') return 'Turin';
				else if (provider === 'OFM') return 'Vienna';
				else if (provider === 'SFI') return 'Stockholm';
				else if (provider === 'TTE') return 'Athens';
				else return provider;
			};
		})
		;

	// The controller
	function SearchController($scope, $log, $document, $state, $stateParams, DataService, CodelistService, noty, $uibModal) {
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
		self.inputProvider = null;
		self.advancedSearch = false;

		// list of match field
		self.matchFields = ['title', 'keyword', 'description', 'contributor'];
		// Selected fields
		self.selectedMatchFields = [];
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

		self.alerts = [];
		self.closeAlert = function(index) {
			self.alerts.splice(index, 1);
		};

		// initialise countries list
		self.countries = [];
		var lang = 'en'; // put here the language chosen by the user
		CodelistService.loadTerms(lang, "countries").then(function(data) {
			self.countries = data;
		});

		self.searchCreations = function() {
			var request_data = {};
			var isValid = true;
			if (self.advancedSearch) {
				request_data = {
					"filter": {
						"type": self.inputItemType,
						"provider": self.inputProvider,
						"country": self.inputCountry,
						"iprstatus": self.inputIPRStatus,
						"yearfrom": $scope.search.year_min.toString(),
						"yearto": $scope.search.year_max.toString(),
					}
				};
				if (self.inputTerm !== '') {
					if (self.selectedMatchFields.length === 0) {
						isValid = false;
					}
					request_data.match = {
						"term": self.inputTerm,
						"fields": self.selectedMatchFields
					};
				}
			} else {
				var simple_match_term = self.inputTerm === '' ? '*' : self.inputTerm;
				request_data = {
					"match": {
						"term": simple_match_term,
						"fields": ["title"],
					},
				};
			}
			/*if (!isValid) {
				self.alerts.push({msg: 'Invalid search request.'});
				return;
			}*/
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
					var errors = out_data.data.Response.errors;
					angular.forEach(errors, function(error) {
						self.alerts.push({
							msg: error
						});
					});
					self.loading = false;
					self.studyCount = 0;
					self.loadResults = false;
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
		$scope.providers = providers;
		self.inputItemType = "video";
		$scope.cleanupFilters = function() {
			self.inputItemType = "video";
			self.inputProvider = "";
		};

		// move codelist provision in a service
		self.iprstatuses = iprstatuses;

	}

	function NewSearchController($scope, DataService, NgMap, $timeout, $filter, GeoCoder, GOOGLE_API_KEY, VocabularyService, noty, ivhTreeviewMgr) {
		var sc = this;
		sc.displayMode = "Grid";
		sc.loading = false;
		sc.cities = {
			options:  [],
			selected: null
		};
		angular.forEach(providers, function(p){
			sc.cities.options.push(p.city.name);
		});

		sc.inputTerm = "";
		// list of match field
		sc.matchFields = ['title', 'keyword', 'description', 'contributor'];
		// Selected fields
		sc.selectedMatchFields = ['title'];
		// Toggle selection for a given field by name
		sc.toggleMatchFieldSelection = function(matchField) {
			var idx = self.selectedMatchFields.indexOf(matchField);
			// Is currently selected
			if (idx > -1) {
				sc.selectedMatchFields.splice(idx, 1);
			}
			// Is newly selected
			else {
				sc.selectedMatchFields.push(matchField);
			}
		};

		// move codelist provision in a service
		sc.iprstatuses = {
			options:  iprstatuses,
			selected: null
		};

		sc.vocabulary = [];
		VocabularyService.loadTerms().then(function(data) {
			sc.vocabulary = data;
		});

		sc.terms = [];
		sc.loadVocabularyTerms = function(query) {
			return $filter('matchTerms')(sc.vocabulary, query);
		};

		// custom treeview tpl
		sc.treeviewTpl = [
			'<div>',
			  '<span ivh-treeview-toggle>',
			    '<span ivh-treeview-twistie></span>',
			  '</span>',
			  '<span ng-if="trvw.useCheckboxes() && trvw.isLeaf(node)" ivh-treeview-checkbox></span>',
			  '<span class="ivh-treeview-node-label" ivh-treeview-toggle>',
			    '{{:: trvw.label(node)}}',
			  '</span>',
			  '<div ivh-treeview-children class="ivh-treeview-children"></div>',
			'</div>'
		].join('\n');

		sc.toggleTerm = function(node) {
			if (node.selected) {
				// add tag
				sc.terms.push({iri: node.id, label: node.label});
			} else {
				sc.terms = _.reject(sc.terms, function(el) { return el.label === node.label; });
			}
		};

		sc.selectTreeviewNode = function(tag) {
			if (tag.iri !== undefined) {
				// console.log('select treeview by node id: ' + tag.iri);
				ivhTreeviewMgr.select(sc.vocabulary, tag.iri);
			}
		};

		self.deselectTreeviewNode = function(tag) {
			if (tag.iri !== undefined) {
				// console.log('deselect treeview by node id: ' + tag.iri);
				ivhTreeviewMgr.deselect(sc.vocabulary, tag.iri);
			}
		};

		sc.itemType = {
			video: true,
			image: true,
			text: false
		};
		$scope.$watch('sc.itemType', function(newValue, oldValue) {
			if (newValue !== oldValue) {
				if (newValue.video && newValue.image) sc.filter.type='all';
				else if (newValue.video) sc.filter.type='video';
				else if (newValue.image) sc.filter.type='image';
				else if (newValue.text) sc.filter.type='text';
			}
		}, true);

		sc.minProductionYear = 1890;
		sc.maxProductionYear = 1999;
		sc.resetFilters = function() {
			sc.inputTerm = "";
			sc.selectedMatchFields = ['title'];
			sc.terms = [];
			sc.itemType.video = true;
			sc.itemType.image = true;
			sc.iprstatuses.selected = null;
			sc.cities.selected = null;
			sc.filter = {
				type: 'all',
				provider: null,
				country: null,
				iprstatus: null,
				yearfrom: sc.minProductionYear,
				yearto: sc.maxProductionYear,
				terms: sc.terms
			};
			ivhTreeviewMgr.deselectAll(sc.vocabulary);
			ivhTreeviewMgr.collapseRecursive(sc.vocabulary, sc.vocabulary);
		};
		sc.resetFilters();

		$scope.$watch('sc.cities.selected', function(newValue, oldValue) {
			if (newValue !== oldValue) {
				var res = null;
				// "Athens", "Bologna", "Brussels", "Copenhagen", "Frankfurt am Main", "Barcelona", "Turin", "Vienna", "Stockholm"
				if (newValue === 'Athens') { res = 'TTE'; }
				else if(newValue === 'Bologna') { res = 'CCB'; }
				else if(newValue === 'Brussels') { res = 'CRB'; }
				else if(newValue === 'Copenhagen') { res = 'DFI'; }
				else if(newValue === 'Frankfurt am Main') { res = 'DIF'; }
				else if(newValue === 'Barcelona') { res = 'FDC'; }
				else if(newValue === 'Turin') { res = 'MNC'; }
				else if(newValue === 'Vienna') { res = 'OFM'; }
				else if(newValue === 'Stockholm') { res = 'SFI'; }
				sc.filter.provider = res;
				// console.log('filter by city for archive: ' + sc.filter.provider);
			}
		});
		$scope.$watch('sc.iprstatuses.selected', function(newValue, oldValue) {
			if (newValue !== oldValue) {
				sc.filter.iprstatus = newValue;
			}
		});

		// pagination
		sc.pager = {
			options: [12, 24, 36, 48],
			maxSize: 5
		};
		sc.resetPager = function() {
			sc.pager.currentPage = 1;
			sc.pager.itemsPerPage = sc.pager.options[0];
		};
		sc.resetPager();

		sc.googleMapsUrl = GOOGLE_API_KEY;
		sc.mapLoaded = false;
		sc.mapZoom = 4;
		sc.mapCenter = [50.00,20.34];
		sc.dynMarkers = [];
		sc.mapTags = [];

		sc.centerEurope = function() {
			sc.mapZoom = 4;
			sc.mapCenter = [50.00,20.34];
			var pt = new google.maps.LatLng(sc.mapCenter[0], sc.mapCenter[1]);
			sc.map.setCenter(pt);
			sc.map.setZoom(sc.mapZoom);
		};

		sc.centerChanged = function(event) {
			if (!angular.isDefined(sc.map)) { return; }
			$timeout(function() {
				//sc.map.panTo(sc.map.getCenter());
				sc.mapCenter = sc.map.getCenter();
			}, 2000);
		};

		sc.zoomChanged = function(event) {
			if (!angular.isDefined(sc.map)) { return; }
			/*console.log('zoom ' + sc.map.getZoom());*/
		};

		function centerMap(place) {
			if (place === undefined) { return; }
			// console.log(place);
			var lat = place.lat,
				lng = place.lng;
			if (lat === undefined || lng === undefined) { return; }
			var pt = new google.maps.LatLng(lat, lng);
			sc.map.setCenter(pt);
			sc.mapCenter = [lat, lng];
			var bounds = new google.maps.LatLngBounds();
			for (var i = 0; i < place.viewport.length; i++) {
				var latlng = new google.maps.LatLng(place.viewport[i].lat(), place.viewport[i].lng());
				bounds.extend(latlng);
			}
			sc.map.fitBounds(bounds);
		}

		$scope.$watch('sc.inputPlaceDetails', function(newValue, oldValue) {
			if (newValue !== oldValue) {
				centerMap(sc.inputPlaceDetails);
			}
		}, true);

		sc.search = function() {
			sc.loading = true;
			// at the moment search term ONLY in the title
			var request_data = {
				"match": {
					term: "*",
					fields: sc.selectedMatchFields
				}
			};
			// Add filters
			request_data.filter = sc.filter;
			if (sc.inputTerm !== '') {
				request_data.match.term = sc.inputTerm;
			}
			DataService.searchCreations(request_data, sc.pager.currentPage, sc.pager.itemsPerPage).then(
				function(out_data){
					var meta = out_data.data.Meta;
					sc.totalItems = meta.totalItems;
					sc.countByYears = meta.countByYears;
					sc.creations = out_data.data.Response.data;
					NgMap.getMap().then(function(map) {
						sc.map = map;
						// clean up current marker list
						if (sc.markerClusterer !== undefined) {
							sc.markerClusterer.clearMarkers();
						}
						sc.dynMarkers = [];
						if (sc.filter.provider !== null) {
							sc.mapZoom = 14;
							sc.mapCenter = getPosition(sc.filter.provider);
							var cFilter = {
								filter: sc.filter
							};
							if (sc.inputTerm !== '') {
								cFilter.match = {
									term: sc.inputTerm,
									fields: sc.selectedMatchFields
								};
							}
							DataService.getGeoDistanceAnnotations(2, sc.mapCenter, cFilter).then(
								function(response) {
									sc.mapTags = response.data.Response.data;
									var relevantCreations = new Map();
									angular.forEach(sc.mapTags, function(tag, index) {
										var latLng = new google.maps.LatLng(tag.spatial[0], tag.spatial[1]);
										var marker = new google.maps.Marker({
											position: latLng,
											id: tag.iri,
											name: tag.name,
											sources: tag.sources
										});
										// update relavant creations
										for (var i=0; i<tag.sources.length; i++) {
											var uuid = tag.sources[i].uuid;
											if(!relevantCreations.has(uuid)) {
												relevantCreations.set(uuid, new Set([tag.iri]));
											} else {
											    relevantCreations.get(uuid).add(tag.iri);
											}
										}

										google.maps.event.addListener(marker, 'click', function() {
											sc.markerTag = marker;
											GeoCoder.geocode({
												'placeId': marker.id
											}).then(function(results) {
												// look outside in order to enrich details for that given place id
												if (results[0]) {
													sc.markerTag.address = results[0].formatted_address;
												} else {
													noty.showWarning('No results found');
												}
											}).catch(function(error) {
												noty.showWarning('Unable to get info for place ID: ' + marker.id);
											}).finally(function(){
												// should we move the center to tag position?
												sc.map.setCenter(sc.markerTag.position);
												sc.map.showInfoWindow('tag-iw', sc.markerTag);
											});

										});
										sc.dynMarkers.push(marker);
									});
									updateMarkers(map);
									sc.loadingMapResults = true;
									DataService.getRelavantCreations(relevantCreations).then(function(response) {
										sc.mapResults = response.data.Response.data;
										// console.log(sc.mapResults);
									}).catch(function(error) {
										noty.showWarning('Unable to retrieve relevant creation on the map. Reason: ' + error);
									}).finally(function() {
										sc.loadingMapResults = false;
									});
								}
							);
						} else {
							// content from all cities represented on a map of Europe
							sc.mapZoom = 4;
							sc.mapCenter = [50.00,20.34];
							// expected content count by providers (i.e. cities)
							if (meta.countByProviders !== undefined) {
								Object.keys(meta.countByProviders).forEach(function(key,index) {
								    // key: the name of the object keyvar position = getPosition(provider);
									var position = getPosition(key);
									if (position === undefined) {
										console.warn("Cannot get position by given key: '" + key + "'");
									} else {
										var latLng = new google.maps.LatLng(position[0], position[1]);
										var count = meta.countByProviders[key];
										for (var i = 0; i < count; i++) {
											sc.dynMarkers.push(new google.maps.Marker({ position: latLng }));
										}
									}
								});
							} else {
								console.warn('expected content count by provider');
							}
							// clean up relevant creations under the map
							sc.mapResults = [];
							updateMarkers(map);
						}
						
					});
				},
				function(out_data) {
					var errors = out_data.data.Response.errors;
					angular.forEach(errors, function(error) {
						sc.alerts.push({
							msg: error
						});
					});
					noty.extractErrors(out_data, noty.ERROR);
				}).finally(function() {
					sc.loading = false;
				});
		};
		sc.search();

		function updateMarkers(map) {
			sc.markerClusterer = new MarkerClusterer(
				map, sc.dynMarkers, {
					imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
				});
			sc.mapLoaded = true;
		}

		sc.showInfoWindow = function(marker) {
			console.log(marker);
			sc.markerTag = marker;
			sc.map.showInfoWindow('tag-iw', sc.markerTag);
		};

		// force map resize
		$scope.$watch('sc.displayMode', function(newValue, oldValue) {
			if (newValue === 'Map') {
				$timeout(function() {
					var currCenter = sc.map.getCenter();
					google.maps.event.trigger(sc.map, 'resize');
					sc.map.setCenter(currCenter);
				}, 500);
			}
		}, true);

		sc.setItemsPerPage = function(num) {
			sc.pager.itemsPerPage = num;
			sc.pager.currentPage = 1; //reset to first page
			sc.search();
		};
		sc.pageChanged = function() {
			sc.search();
		};

		// timeline
		sc.timeline = {};
		sc.timeline.range = [1890, 1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990];
		sc.updateFilterByDecade = function(decade) {
			sc.filter.yearfrom = decade;
			sc.filter.yearto = decade + 9;
		};
	}

})();