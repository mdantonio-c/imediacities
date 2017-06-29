(function() {
	'use strict';

	var app = angular.module('web')
		.controller('SearchController', SearchController)
		.controller('WatchController', WatchController)
		.controller('MapController', MapController)
		.controller('ModalInstanceCtrl', ModalInstanceCtrl)
		.controller('ModalResultInstanceCtrl', ModalResultInstanceCtrl);

	/*modal view storyboard factory definition*/
	app.factory('modalFactory', function($uibModal) {
		return {
			open: function(size, template, params) {
				return $uibModal.open({
					animation: false,
					templateUrl: template || 'myModalContent.html',
					controller: 'ModalResultInstanceCtrl',
					controllerAs: '$ctrl',
					size: size,
					resolve: {
						params: function() {
							return params;
						}
					}
				});
			}
		};
	});

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
		.filter('trustUrl', function($sce) {
			return function(url) {
				return $sce.trustAsResourceUrl(url);
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
		})
		.filter('salientEstimates', function() {
			return function(estimates, threshold) {
				threshold = typeof threshold !== 'undefined' ? threshold : 0.5;
				var res = {};
				var h_avg = 0,
					h_key,
					found = false;
				for (var p in estimates) {
					// skip loop if the property is from prototype
					if (!estimates.hasOwnProperty(p)) continue;

					var avg = estimates[p][0];
					var key = p.replace(/_/g, " ");
					if (avg >= threshold) {
						res[key] = avg;
						found = true;
					}

					if (!found && avg > h_avg) {
						h_key = key;
						h_avg = avg;
					}
				}
				if (Object.keys(res).length === 0) {
					res[h_key] = h_avg;
				}
				return res;
			};
		});

	app.directive('scrollOnClick', function() {
			return {
				//restrict: 'A',
				link: function($scope, $elm) {
					$elm.on('click', function() {
						$(".scrollmenu").animate({
							scrollLeft: ($elm[0].offsetLeft-($elm[0].parentNode.parentNode.scrollWidth/2))
						}, "slow");
						// play video from selected shot
						var duration = $elm[0].firstElementChild.attributes.duration.value;
						var nshots = $elm[0].firstElementChild.attributes.nshots.value;
						var progr = $elm[0].firstElementChild.attributes.progr.value;
						var myVid = angular.element(window.document.querySelector('#videoarea'));
						var currtime = $elm[0].firstElementChild.attributes.timestamp.value;
						currtime = currtime.split("-")[0];
						var hours = currtime.split(":")[0];
						var mins = currtime.split(":")[1];
						var secs = currtime.split(":")[2];
						var cdate = new Date(0, 0, 0, hours, mins, secs);
						var times = (secs * 1) + (mins * 60) + (hours * 3600); //convert to seconds

						//myVid[0].pause();
						myVid[0].currentTime = times+5;
						myVid[0].play();

					});
				}
			};
		})
		/*app.directive('scrollOnClick', function() { //carousel version
			return {
				//restrict: 'A',
				link: function($scope, $elm) {
					$elm.on('click', function() {
						//alert($elm[0].parentNode.className);
						$(".scrollmenu").animate({
							scrollLeft: $elm[0].offsetLeft
						}, "slow");
						// play video from selected shot
						var duration = $elm[0].attributes.duration.value;
						var nshots = $elm[0].attributes.nshots.value;
						var progr = $elm[0].attributes.progr.value;
						var myVid = angular.element(window.document.querySelector('#videoarea'));
						var currtime = $elm[0].attributes.timestamp.value;
						currtime = currtime.split("-")[0];
						var hours = currtime.split(":")[0];
						var mins = currtime.split(":")[1];
						var secs = currtime.split(":")[2];
						var cdate = new Date(0, 0, 0, hours, mins, secs);
						var times = (secs * 1) + (mins * 60) + (hours * 3600); //convert to seconds

						//myVid[0].pause();
						myVid[0].currentTime = times+5;
						myVid[0].play();

					});
				}
			};
		})*/
		.directive('modalMovable', ['$document',
    	function($document) {
        return {
            restrict: 'AC',
            link: function(scope, iElement, iAttrs) {
                var startX = 0,
                    startY = 0,
                    x = 0,
                    y = 0;

                var dialogWrapper = iElement.parent();

                dialogWrapper.css({
                    position: 'relative'
                });

                dialogWrapper.on('mousedown', function(event) {
                    // Prevent default dragging of selected content
                    event.preventDefault();
                    startX = event.pageX - x;
                    startY = event.pageY - y;
                    $document.on('mousemove', mousemove);
                    $document.on('mouseup', mouseup);
                });

                function mousemove(event) {
                    y = event.pageY - startY;
                    x = event.pageX - startX;
                    dialogWrapper.css({
                        top: y + 'px',
                        left: x + 'px'
                    });
                }

                function mouseup() {
                    $document.unbind('mousemove', mousemove);
                    $document.unbind('mouseup', mouseup);
                	}
            	}
        	};
    		}
		])
		.directive('pagination', function() {
			return {
				restrict: 'E',
				scope: {
					numPages: '=',
					currentPage: '=',
					onSelectPage: '&'
				},
				templateUrl: 'pagination.html',
				replace: true,
				link: function(scope) {
					scope.$watch('numPages', function(value) {
						scope.pages = [];
						for (var i = 1; i <= value; i++) {
							scope.pages.push(i);
						}
						if (scope.currentPage > value) {
							scope.selectPage(value);
						}
					});
					scope.noPrevious = function() {
						return scope.currentPage === 1;
					};
					scope.noNext = function() {
						return scope.currentPage === scope.numPages;
					};
					scope.isActive = function(page) {
						return scope.currentPage === page;
					};

					scope.selectPage = function(page) {
						if (!scope.isActive(page)) {
							scope.currentPage = page;
							scope.onSelectPage({
								page: page
							});
						}
					};

					scope.selectPrevious = function() {
						if (!scope.noPrevious()) {
							scope.selectPage(scope.currentPage - 1);
						}
					};
					scope.selectNext = function() {
						if (!scope.noNext()) {
							scope.selectPage(scope.currentPage + 1);
						}
					};
				}
			};
		});

	function getElement(event) {
		return angular.element(event.srcElement || event.target);
	}

	// The controller
	function SearchController($scope, $log, $document, $state, $stateParams, DataService, noty, $uibModal) {
		var self = this;

		self.showmesb = false;
		self.viewlogo = true;
		self.showmese = false;
		//self.showmepg = true;

		$scope.currentPage = 1;
		$scope.noOfPages = 1;

		/*pagination*/
		$scope.setPage = function(currp, nump) {
			$scope.vmin = (currp - 1) * nump;
			$scope.vmax = nump;
		};

		// $scope.$watch('currentPage', $scope.setPage($scope.currentPage, $scope.noOfPages));

		self.videos = [];

		self.loading = false;
		self.inputTerm = "";
		self.searchVideos = function() {
			var request_data = {
				"type": "video",
				"term": ""
			};
			request_data.term = self.inputTerm === '' ? '*' : self.inputTerm;
			// console.log('search videos with term: ' + request_data.term);
			self.loadResults = false;
			self.loading = true;
			self.showmese = true;
			DataService.searchVideos(request_data).then(
				function(out_data) {
					self.videos = out_data.data;
					self.loading = false;
					self.loadResults = true;
					self.showmese = false;
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


	}

	function WatchController($log, $document, $uibModal, $stateParams, DataService, noty) {

		var self = this;
		self.showmesb = false;
		self.showmeli = true;
		var vid = $stateParams.v;
		self.video = $stateParams.meta;

		// Initializing values
		var onplaying = false;
		var onpause = false;

		var myVid = angular.element(window.document.querySelector('#videoarea'));

		// On video playing toggle values
		myVid[0].onplaying = function() {
    		onplaying = true;
    		if (!onpause){
    			myVid[0].pause();
    		}
		};

		// On video pause toggle values
		myVid[0].onpause = function() {
    		onplaying = false;
    		onpause = true;
		};

		// Play video function
		function playVid(video) {      
    	if (video.paused && !onplaying) {
    		video.currtime = '3';
        	video.play();
    		}
		} 

		// Pause video function
		function pauseVid(video) {     
    	if (!video.paused && !onpause) {
        	video.pause();
    		}
		}

		self.items = [];
		self.shots = [];
		self.loadVideoShots = function(vid) {
			DataService.getVideoShots(vid).then(
				function(response) {
					self.shots = response.data;
					for (var i = 0; i < self.shots.length; i++) {
						var thumblink = self.shots[i].links.thumbnail;
						var start_frame = self.shots[i].attributes.start_frame_idx;
						var timestamp = self.shots[i].attributes.timestamp;
						var frameshot = [];
						frameshot[0] = start_frame;
						frameshot[1] = self.video.relationships.item[0].attributes.duration;
						frameshot[2] = parseInt(self.shots[i].attributes.duration);
						frameshot[3] = self.shots.length;
						frameshot[4] = i;
						frameshot[5] = timestamp;
						frameshot[6] = thumblink;

						self.items.push(frameshot);

						self.showmesb = true; //enable storyboard button
						self.showmeli = false; //hide loading video bar

						if (i === 0) {
							/*once we have all data and metadata the video start playing*/
							var myVid = angular.element(window.document.querySelector('#videoarea'));
							playVid(myVid[0]);
							onpause = false;
    					}
					}
				});
		};

		self.loadMetadataContent = function(vid) {
			self.loading = true;
			// console.log('loading metadata content');
			DataService.getVideoMetadata(vid).then(
				function(response) {
					self.video = response.data[0];
					self.loading = false;
					self.loadVideoShots(vid);
				},
				function(error) {
					self.loading = false;
					noty.extractErrors(error, noty.ERROR);
				});
		};

		if (!$stateParams.meta) {
			self.loadMetadataContent(vid);
		} else {
			self.loadVideoShots(vid);
		}

		self.selectedVideoId = vid;
		self.animationsEnabled = true;
		self.showStoryboard = function(size, parentSelector) {
			var parentElem = parentSelector ? 
      			angular.element($document[0].querySelector('#video-wrapper ' + parentSelector)) : undefined;
      		var modalInstance = $uibModal.open({
				animation: self.animationsEnabled,
				templateUrl:'myModalContent.html',
				controller: 'ModalInstanceCtrl',
				controllerAs: '$ctrl',
				size: size,
				appendTo: parentElem,
				resolve: {
					params: function() {
						var params = {};
						angular.extend(params, {
							'videoid': self.selectedVideoId,
							'summary': self.video.links.summary
						});
						return params;
					},
					shots: function() {
						return self.shots;
					}
				}
			});
		};

		/*self.jumpToShot = function(selectedShot) {
			var row = selectedShot.row;
			if (row !== 0) {
				// ignore 'Duration' row
				var time1 = self.videoTimeline.data.rows[row].c[2].v.getSeconds();
				var time2 = self.videoTimeline.data.rows[row].c[3].v.getSeconds();

				// play video from selected shot
				var myVid = angular.element($document[0].querySelector('#videoarea'));
				myVid[0].currentTime = time1;
				myVid[0].play();
			}
		};*/

	}

	function MapController($scope, NgMap, NavigatorGeolocation, GeoCoder, $timeout) {

		var vm = this;
		vm.videolat = null;
		vm.videolng = null;
		vm.locname = null;
		vm.zoom = 15;

		vm.init = function(location) {
			// FIXME what is the default?
			vm.location = location === undefined ? 'Bologna, IT' : location;
		};

		NgMap.getMap("videomap").then(function(map) {
			// start geocoding and get video coordinates
			GeoCoder.geocode({
					address: vm.location
				})
				.then(function(result) {
					vm.videolat = result[0].geometry.location.lat();
					vm.videolng = result[0].geometry.location.lng();
					vm.locname = result[0].address_components[0].long_name;
				});
		});

		// force map resize
		$timeout(function() {
			NgMap.getMap({
				id: 'videomap'
			}).then(function(map) {
				var currCenter = map.getCenter();
				google.maps.event.trigger(map, 'resize');
				map.setCenter(currCenter);
			});
		}, 3000);

		vm.googleMapsUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI";
	}



	// storyboard modal view
	// Please note that $modalInstance represents a modal window (instance) dependency.
	// It is not the same as the $uibModal service used above.

	function ModalInstanceCtrl($uibModalInstance, shots, params, modalFactory) {
		var self = this;

		// filling the storyboard with the image shots

		self.videoid = params.videoid;
		self.summary = params.summary;
		self.shots = [];

		angular.forEach(shots, function(shot) {

/*			self.camera = [];
			var annotations = shot.annotations;
			var camattr = annotations[0].attributes;
			var first = true;

			angular.forEach(camattr, function(value,key) {

				var motion = value;	

				var cv = parseFloat(value[1]).toFixed(2);
    			var av = parseFloat(0.3).toFixed(2);

				if ((cv < av) && first) {first = false; self.camera.push(key+' '+motion);}

			});*/


			var framerange = shot.attributes.start_frame_idx + ' - ' + (shot.attributes.end_frame_idx - 1)
			self.shots.push({
				'thumb': shot.links.thumbnail,
				'number': shot.attributes.shot_num,
                'framerange': framerange,
				'timestamp': shot.attributes.timestamp,
				'duration': parseInt(shot.attributes.duration),
				'camera': shot.annotations[0].attributes
			});
		});

		self.showSummary = function() {
			modalFactory.open('lg', 'summary.html', {
				animation: false,
				summary: self.summary
			});
		};

		self.cancel = function() {
			$uibModalInstance.dismiss('cancel');
		};

	}

	function ModalResultInstanceCtrl($uibModalInstance, params) {
		var self = this;
		self.summary = params.summary;

		self.cancel = function() {
			$uibModalInstance.dismiss('cancel');
		};
	}

})();
