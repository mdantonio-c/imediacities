(function() {
	'use strict';

	var app = angular.module('web')
		.controller('geoTagController', geoTagController)
		.controller('geoResultController', geoResultController)
		.controller('WatchController', WatchController)
		.controller('MapController', MapController);

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
	}).factory('myModalGeoFactory', function($uibModal) { /*modal view add location tag definition*/
		return {
			open: function(size, template, params) {
				return $uibModal.open({
					animation: true,
					templateUrl: template || 'myModalGeoCode.html',
					controller: 'geoTagController',
					size: size,
					resolve: {
						params: function() {
							return params;
						}
					}
				});
			}
		};
	}).factory('myGeoConfirmFactory', function($uibModal) {
		return {
			open: function(size, template, params) {
				return $uibModal.open({
					animation: true,
					templateUrl: template || 'result.html',
					controller: 'geoResultController',
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

	app.service('sharedProperties', function() {
		var startTime = 'test start value';
		var endTime = 'test end value';
		var labelTerm = 'test label value';
		var group = 'test label value';
		var shotPNG = 'test label value';
		var videoId = '';
		var IRI = '';
		var shotId = '';
		var alternatives = null;
		var latitude = '';
		var longitude = '';
		var formatted = '';
		var photoref = '';
		var shotnum = '';

		return {
			getStartTime: function() {
				return startTime;
			},
			getEndTime: function() {
				return endTime;
			},
			getLabelTerm: function() {
				return labelTerm;
			},
			getFormAddr: function() {
				return formatted;
			},
			getGroup: function() {
				return group;
			},
			getShotPNG: function() {
				return shotPNG;
			},
			getVideoId: function() {
				return videoId;
			},
			getIRI: function() {
				return IRI;
			},
			getPhotoRef: function() {
				return photoref;
			},
			getShotId: function() {
				return shotId;
			},
			getLatitude: function() {
				return latitude;
			},
			getLongitude: function() {
				return longitude;
			},
			getAlternatives: function() {
				return alternatives;
			},
	        getShotNum: function() {
	            return shotnum;
	        },
			setStartTime: function(value) {
				startTime = value;
			},
			setEndTime: function(value) {
				endTime = value;
			},
			setLat: function(value) {
				latitude = value;
			},
			setLong: function(value) {
				longitude = value;
			},
			setLabelTerm: function(value) {
				labelTerm = value;
			},
			setFormAddr: function(value) {
				formatted = value;
			},
			setGroup: function(value) {
				group = value;
			},
			setShotPNG: function(value) {
				shotPNG = value;
			},
			setVideoId: function(value) {
				videoId = value;
			},
			setIRI: function(value) {
				IRI = value;
			},
			setShotId: function(value) {
				shotId = value;
			},
	        setShotNum: function(value){
	        	shotnum = value;
	        },			
			setPhotoRef: function(value) {
				photoref = value;
			},
			setAlternatives: function(value) {
				alternatives = value;
			}
		};
	});

	app.filter('trustUrl', function($sce) {
			return function(url) {
				return $sce.trustAsResourceUrl(url);
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
		})
		.filter('termfilter', [function() {
			return function(items, searchText) {
				var filtered = [];

				angular.forEach(items, function(item) {
					var stringtos = item.labels.en;
					if ((stringtos.indexOf(searchText) >= 0) || (searchText === '')) { // matches part of the word, e.g. 'England'
						item.show = true;
						filtered.push(item);
					}
				});
				return filtered;
			};
		}])
		.filter('groupfilter',[ function () {
				return function(items, options) {
				    var filtered = [];            

				    angular.forEach(items, function(item) {
				    	var stringtos = item.group;
				    	angular.forEach(options[1], function(group) {
				    		var stringgroup = options[0][group].Display;
				        	if((stringtos === stringgroup) || (stringgroup === '')){ 
				            	filtered.push(item);						        
				        	}
				    	});
				    });
				    return filtered;
				};
			}])
			.filter('timefilter',[ function () {
				return function(items, currentTime) {
				    var filtered = [];            

				    angular.forEach(items, function(item) {
			    		var startT = item.startT;
			    		var endT = item.endT;						    		
			        	if((currentTime >= startT) && (currentTime <= endT)){ 
			            	filtered.push(item);						        
			        	}
				    });
				    return filtered;
				};
		}]);


	app.directive('scrollStoryOnClick', function() {
		return {
			//restrict: 'A',
			link: function($scope, $elm) {
				$elm.on('click', function() {
					if ($elm[0].parentNode.className == "scrollmenu") {
						$(".scrollmenu").animate({
							scrollLeft: ($elm[0].offsetLeft - ($elm[0].parentNode.parentNode.scrollWidth / 2))
						}, "slow");
					}
					// play video from selected shot
					var duration = $elm[0].firstElementChild.attributes.duration.value;
					var nshots = $elm[0].firstElementChild.attributes.nshots.value;
					var progr = $elm[0].firstElementChild.attributes.progr.value;
					var myVid = angular.element(window.document.querySelector('#videoarea'));
					var currtime = $elm[0].firstElementChild.attributes.timestamp.value;

					var times = convertTime(currtime);

					//myVid[0].pause();
					myVid[0].currentTime = times;
					myVid[0].play();

				});
			}
		};
	});
	app.directive('scrollOnClick', function() { //carousel version
		return {
			//restrict: 'A',
			link: function($scope, $elm) {
				$elm.on('click', function() {
					//alert($elm[0].parentNode.className);
					if ($elm[0].parentNode.className == "scrollmenu") {
						$(".scrollmenu").animate({
							scrollLeft: $elm[0].offsetLeft
						}, "slow");
					}
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
					myVid[0].currentTime = times;
					myVid[0].play();

				});
			}
		};
	});

	app.directive('dropdown', function($document) {
		return {
			restrict: "C",
			link: function(scope, elem, attr) {

				elem.bind('click', function() {
					elem.toggleClass('dropdown-active');
					elem.addClass('active-recent');
				});

				$document.bind('click', function() {
					if (!elem.hasClass('active-recent')) {
						elem.removeClass('dropdown-active');
					}
					elem.removeClass('active-recent');
				});

			}
		};
	});

	app.directive('ngAutocomplete', ['$parse', '$timeout',
		function($parse, $timeout) {

			function convertPlaceToFriendlyObject(place) {
				var result;
				if (place) {
					result = {};
					for (var i = 0, l = place.address_components.length; i < l; i++) {
						if (i === 0) {
							result.searchedBy = place.address_components[i].types[0];
						}
						result[place.address_components[i].types[0]] = place.address_components[i].long_name;
					}
					result.formattedAddress = place.formatted_address;
					result.lat = place.geometry.location.lat();
					result.lng = place.geometry.location.lng();
					if (place.photos !== undefined) {
						result.photo_reference = place.photos[0].getUrl({
							'maxWidth': 35,
							'maxHeight': 35
						});
					} else {
						result.photo_reference = '';
					}
				}
				return result;
			}

			return {
				restrict: 'A',
				require: 'ngModel',
				link: function($scope, $element, $attrs, $ctrl) {

					if (!angular.isDefined($attrs.details)) {
						throw '<ng-autocomplete> must have attribute [details] assigned to store full address object';
					}

					var getDetails = $parse($attrs.details);
					var setDetails = getDetails.assign;
					var getOptions = $parse($attrs.options);

					//options for autocomplete
					var opts;

					//convert options provided to opts
					var initOpts = function() {
						opts = {};
						if (angular.isDefined($attrs.options)) {
							var options = getOptions($scope);
							if (options.types) {
								opts.types = [];
								opts.types.push(options.types);
							}
							if (options.bounds) {
								opts.bounds = options.bounds;
							}
							if (options.country) {
								opts.componentRestrictions = {
									country: options.country
								};
							}
						}
					};

					//create new autocomplete
					//reinitializes on every change of the options provided
					var newAutocomplete = function() {

						$timeout(function() {

							var gPlace = new google.maps.places.Autocomplete($element[0], opts);
							google.maps.event.addListener(gPlace, 'place_changed', function() {
								$scope.$apply(function() {
									var place = gPlace.getPlace();
									var details = convertPlaceToFriendlyObject(place);
									setDetails($scope, details);
									$ctrl.$setViewValue(details.formattedAddress);
									$ctrl.$validate();
								});
								if ($ctrl.$valid && angular.isDefined($attrs.validateFn)) {
									$scope.$apply(function() {
										$scope.$eval($attrs.validateFn);
									});
								}
							});

						}, 1000);

					};
					newAutocomplete();

					$ctrl.$validators.parse = function(value) {
						var details = getDetails($scope);
						var valid = ($attrs.required === true && details !== undefined && details.lat !== undefined) ||
							(!$attrs.required && (details === undefined || details.lat === undefined) && $element.val() !== '');
						return valid;
					};

					$element.on('keypress', function(e) {
						// prevent form submission on pressing Enter as there could be more inputs to fill out
						if (e.which == 13) {
							e.preventDefault();
						}
					});

					//watch options provided to directive
					if (angular.isDefined($attrs.options)) {
						$scope.$watch($attrs.options, function() {
							initOpts();
							newAutocomplete();
						});
					}

					// user typed something in the input - means an intention to change address, which is why
					// we need to null out all fields for fresh validation
					$element.on('keyup', function(e) {
						//          chars 0-9, a-z                        numpad 0-9                   backspace         delete           space
						if ((e.which >= 48 && e.which <= 90) || (e.which >= 96 && e.which <= 105) || e.which == 8 || e.which == 46 || e.which == 32) {
							var details = getDetails($scope);
							if (details !== undefined) {
								for (var property in details) {
									if (details.hasOwnProperty(property) && property != 'formattedAddress') {
										delete details[property];
									}
								}
								setDetails($scope, details);
							}
							if ($ctrl.$valid) {
								$scope.$apply(function() {
									$ctrl.$setValidity('parse', false);
								});
							}
						}
					});

				}
			};
		}
	]);

	app.directive('multiselect',['$document', function($document){
	return {
	  restrict: 'E',
	  require: '?ngModel',
	  scope: {
	    choices: '=',
	    selected: '='
	  },
	  templateUrl: 'multiselect.html',
	  replace: true,
	  link: function(scope, element, attr){
	      scope.isVisible = false;
	        scope.isChecked = function(item){
	          if(scope.selected.indexOf(item) !== -1){
	            return true;
	          }
	          return false;
	        };
	        scope.toggleCheck = function(item){
	          if(!scope.isChecked(item)){
	            scope.selected.push(item);
	          }else{
	            scope.selected.splice(scope.selected.indexOf(item), 1);
	          }
	        };
	        scope.toggleSelect = function(){
	          scope.isVisible = !scope.isVisible;
	        }
	        
	        element.bind('click', function(event) {
	        event.stopPropagation();      
	        });
	                        
	        $document.bind('click', function(){
	        scope.isVisible = false;
	        scope.$apply();
	        });
	  }
	};
	}]);

	function getElement(event) {
		return angular.element(event.srcElement || event.target);
	}

	function convertTime(currtime) {

		currtime = currtime.split("-")[0];
		var hours = currtime.split(":")[0];
		var mins = currtime.split(":")[1];
		var secs = currtime.split(":")[2];
		var cdate = new Date(0, 0, 0, hours, mins, secs);
		var times = (secs * 1) + (mins * 60) + (hours * 3600); //convert to seconds

		return times;

	}

	function WatchController($scope, $http, $rootScope, $log, $document, $uibModal, $stateParams, DataService, noty, myModalGeoFactory, sharedProperties) {

		var self = this;
		self.showmesb = false;
		self.showmeli = true;
		var vid = $stateParams.v;
		self.video = $stateParams.meta;

		self.inputVocTerm = "";

		/*inizialize address for automplete input tag for geolocation*/
		$scope.vm = {
			address: {}
		};
		/*to visualize annotations in tab table*/
		self.annotations = [];

		/*$scope.expand = function(mitem) {
				mitem.show = !mitem.show;
		}*/

		/*initialize multiselect to filter subtitles*/
		$scope.options = [];
		$scope.selectedOptions = [];
		self.locSubtitle = "";

		self.vocabularyFinal = [];
		self.vocabularyFinal = $http.get('static/assets/vocabulary/vocabulary.json').success(function(data) {
		self.vocabularyFinal = data;
		self.onlyterms = [];

		var pushloc = {Value:0,Display:'location'};
		$scope.options.push(pushloc);

		for (var i=0; i<=self.vocabularyFinal.classes.length-1; i++)
		{
			self.vocabularyFinal.classes[i]["show"] = true;
			for (var k=0; k<=self.vocabularyFinal.classes[i].groups.length-1; k++)
			{
				self.vocabularyFinal.classes[i].groups[k]["show"] = true;
				var topush = {Value:k+1,Display:self.vocabularyFinal.classes[i].groups[k].name};
				$scope.options.push(topush);
				for (var j=0; j<=self.vocabularyFinal.classes[i].groups[k].terms.length-1; j++)
				{
					self.vocabularyFinal.classes[i].groups[k].terms[j]["show"] = true;
					self.onlyterms.push(self.vocabularyFinal.classes[i].groups[k].terms[j]);
				}
			}
		}
		});

		// Initializing values
		self.onplaying = false;
		self.onpause = true;
		var paused = false; //warning, this is a one shot variable, we need it only once loading the search page
		self.showtagtxt = false;

		var myVid = angular.element(window.document.querySelector('#videoarea'));

		self.currentTime = myVid[0].currentTime; //initialize current time
		self.startTagTime = self.currentTime;
		self.currentvidDur = 0;

		// On video playing toggle values
		myVid[0].onplaying = function() {
			self.onplaying = true;
			self.onpause = false;
			self.currentTime = myVid[0].currentTime; //always update current time
			if (!paused) {
				myVid[0].pause();
				paused = true;
			}

			/*updating subtitles*/
			//if (self.videoTimeline != null) $rootScope.$emit('updateSubtitles');

		};

		// On video pause toggle values
		myVid[0].onpause = function() {
			self.onplaying = false;
			self.onpause = true;
		};

		// Play video function
		function playVid(video) {
			if (myVid[0].paused && !self.onplaying) {
				self.onpause = false;
				self.onplaying = true;
				video.currtime = '3';
				video.play();
			}
		}

		// Pause video function
		self.pauseVid = function() {
			if ((!myVid[0].paused || !self.onpause)) {
				self.onpause = true;
				self.onplaying = false;
				myVid[0].pause();
			} else if (myVid[0].paused && self.onpause) {
				self.onpause = false;
				self.onplaying = true;
				self.showtagtxt = false;
				myVid[0].play();
			}
		};

		$rootScope.checkAnnotation = function(times1, times2, group, labelterm) {
			/*first check if this annotation already esists in the timeline cache array*/
			var timelinerows = self.videoTimeline.data.rows;
			var foundterm = false;
			for (var k = 0; k <= timelinerows.length - 1; k++) {
				var timel1 = timelinerows[k].c[2].v;
				var timel2 = timelinerows[k].c[3].v;

				var t1 = timel1.getHours() + ':' + timel1.getMinutes() + ':' + timel1.getSeconds();
				var t2 = timel2.getHours() + ':' + timel2.getMinutes() + ':' + timel2.getSeconds();
				var time1c = convertTime(t1);
				var time2c = convertTime(t2);

				/*same interval of this annotation set*/
				if ((parseInt(times1) == time1c) && (parseInt(times2) == time2c)) {
					var acategory = timelinerows[k].c[0].v;
					var aterm = timelinerows[k].c[1].v;
					if ((acategory == group) && (aterm == labelterm)) {
						/*the term has been already added in the timeline cache*/
						foundterm = true;
						if (group == 'location') myModalGeoFactory.open('lg', 'locationFoundModal.html');
						else myModalGeoFactory.open('lg', 'termFoundModal.html');
					}

				}
			}
			return foundterm;
		};

		self.manualtag = function(group, labelterm, tiri, alternatives) {
			if (self.onpause && !self.onplaying) {
				self.startTagTime = myVid[0].currentTime; //set initial tag frame current time

				for (var i = 0; i <= self.items.length - 1; i++) {
					var pngshot = self.items[i][6];
					var shotid = self.items[i][7];
					var shotnum = self.items[i][4];

					var time1 = self.items[i][5];
					if (i < self.items.length - 1) {
						var time2 = self.items[i + 1][5];
						var currtime2 = time2.split("-")[0];
						var hours2 = currtime2.split(":")[0];
						var mins2 = currtime2.split(":")[1];
						var secs2 = currtime2.split(":")[2];
						//var cdate = new Date(0, 0, 0, hours, mins, secs);
						var times2 = (secs2 * 1) + (mins2 * 60) + (hours2 * 3600); //convert to seconds
					} else {
						var times2 = self.items[i][1];
					}

					var currtime1 = time1.split("-")[0];
					var hours1 = currtime1.split(":")[0];
					var mins1 = currtime1.split(":")[1];
					var secs1 = currtime1.split(":")[2];
					//var cdate = new Date(0, 0, 0, hours, mins, secs);
					var times1 = (secs1 * 1) + (mins1 * 60) + (hours1 * 3600); //convert to seconds

					if (self.startTagTime >= times1 && self.startTagTime <= times2) {

						sharedProperties.setVideoId($stateParams.v);
						sharedProperties.setStartTime(times1);
						sharedProperties.setEndTime(times2);
						sharedProperties.setGroup(group);
						sharedProperties.setLabelTerm(labelterm);
						sharedProperties.setAlternatives(alternatives);
						sharedProperties.setIRI(tiri);
						sharedProperties.setShotPNG(pngshot);
						sharedProperties.setShotId(shotid);
						sharedProperties.setShotNum(shotnum+1);

						var foundterm = false;

						if (group != 'location') {
							foundterm = $rootScope.checkAnnotation(times1, times2, group, labelterm);
							/*if the term is a new term*/
							if (!foundterm) {
								myModalGeoFactory.open('lg', 'myModalVocab.html');
							}
						} //if group is not location
						else if (group == 'location') myModalGeoFactory.open('lg', 'myModalGeoCode.html');
					}
				}
			}
		};

		self.items = [];
		self.shots = [];
		self.slideSize = 0;
		self.loadVideoShots = function(vid, vduration) {
			DataService.getVideoShots(vid).then(
				function(response) {
					self.shots = response.data;
					self.storyshots = [];
					self.slideSize = self.shots.length / 9;
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
						frameshot[7] = self.shots[i].id;

						self.items.push(frameshot);

						self.showmesb = true; //enable storyboard button
						self.showmeli = false; //hide loading video bar

						if (i === 0) {
							/*once we have all data and metadata the video start playing*/
							var myVid = angular.element(window.document.querySelector('#videoarea'));
							playVid(myVid[0]);
						}

						//timeline definition
						self.vduration = vduration;

						var minutes = 0,
							hours = 0;
						var seconds = vduration;
						if (seconds / 60 > 0) {
							minutes = parseInt(seconds / 60, 10);
							seconds = seconds % 60;
						}
						if (minutes / 60 > 0) {
							hours = parseInt(minutes / 60, 10);
							minutes = minutes % 60;
						}

						var format = 'mm:ss';

						self.tlineW = '100%';
						if (seconds >= 60) {
							self.tlineW = '100%';
							format = 'ss';
						}
						if (minutes >= 15) {
							self.tlineW = '200%';
							format = 'mm:ss';
						}
						if (minutes >= 60) {
							self.tlineW = '200%';
							format = 'HH:mm:ss';
						}

						/*configuration*/
						var videoTimeline = {
							"type": "Timeline",
							"cssStyle": "height: 100%; width: 100%;",
							//"displayed": false,
							"options": {
								timeline: {
									showRowLabels: true,
									colorByRowLabel: true
								},
								avoidOverlappingGridLines: false,
								hAxis: {
									minValue: new Date(0, 0, 0, 0, 0, 0),
									maxValue: new Date(0, 0, 0, hours, minutes, seconds),
									format: format
								}
							}
						};

						// add data to the timeline
						videoTimeline.data = {
							"cols": [{
								id: "category",
								label: "Category",
								type: "string"
							}, {
								id: "tag",
								label: "Tag",
								type: "string"
							}, {
								id: "start",
								label: "Start",
								type: "date"
							}, {
								id: "end",
								label: "End",
								type: "date"
							}],
							"rows": []
						};

						/*videoTimeline.data.rows.push({c: [
					    	   {v: "area"},
					    	   {v: "Porta Saragozza"},
					   	       {v: new Date(0,0,0,0,0,self.outside.split('-')[0])},
					   		   {v: new Date(0,0,0,0,0,self.outside.split('-')[1])}
							]});*/

						self.videoTimeline = videoTimeline;
					}
					/*print storyboard*/
					angular.forEach(self.shots, function(shot) {

						/*self.camera = [];
						var annotations = shot.annotations;
						var camattr = annotations[0].attributes;
						var first = true;

						angular.forEach(camattr, function(value,key) {

							var motion = value;	

							var cv = parseFloat(value[1]).toFixed(2);
			    			var av = parseFloat(0.3).toFixed(2);

							if ((cv < av) && first) {first = false; self.camera.push(key+' '+motion);}

						});*/

						if ((shot.attributes != undefined) && (shot.attributes.start_frame_idx != undefined)) {
							var framerange = shot.attributes.start_frame_idx + ' - ' + (shot.attributes.end_frame_idx - 1)
							self.storyshots.push({
								'thumb': shot.links.thumbnail,
								'number': shot.attributes.shot_num + 1,
								'framerange': framerange,
								'timestamp': shot.attributes.timestamp,
								'duration': parseInt(shot.attributes.duration),
								'camera': shot.annotations[0].attributes
							});
						}
					});
				});
		};

		self.loadVideoAnnotations = function(vid, vduration) {
			DataService.getVideoAnnotations(vid).then(
				function(response) {

					var resp = response;

				});
		};


		self.loadMetadataContent = function(vid) {
			self.loading = true;
			// console.log('loading metadata content');
			DataService.getVideoMetadata(vid).then(
				function(response) {
					self.video = response.data[0];
					self.currentvidDur = self.video.relationships.item[0].attributes.duration;

					setTimeout(function() {
						$scope.$apply(function() {
							self.loading = false;
							self.loadVideoShots(vid, self.currentvidDur);
							self.loadVideoAnnotations(vid, self.currentvidDur);
						});
					}, 2000);

				},
				function(error) {
					self.loading = false;
					noty.extractErrors(error, noty.ERROR);
				});
		};

		if (!$stateParams.meta) {
			self.loadMetadataContent(vid);
		} else {
			var vidDur = $stateParams.meta.relationships.item[0].attributes.duration;
			self.loadVideoShots(vid, vidDur);
		}

		self.selectedVideoId = vid;
		self.animationsEnabled = true;

		self.jumpToShot = function(selectedShot) {
			var row = selectedShot.row;

			var time1 = self.videoTimeline.data.rows[row].c[2].v;
			var time2 = self.videoTimeline.data.rows[row].c[3].v;

			var t1 = time1.getHours() + ':' + time1.getMinutes() + ':' + time1.getSeconds();
			var t2 = time2.getHours() + ':' + time2.getMinutes() + ':' + time2.getSeconds();
			var time1c = convertTime(t1);
			var time2c = convertTime(t2);

			// play video from selected shot
			var myVid = angular.element($document[0].querySelector('#videoarea'));
			myVid[0].currentTime = time1c;
			myVid[0].play();
		};

		self.jumpToShotFromAnnotation = function(startT) {
			// play video from selected shot
			var myVid = angular.element(window.document.querySelector('#videoarea'));
			myVid[0].currentTime = parseInt(startT);
			myVid[0].play();
		};

		self.getTagMenu = function(event) {
			var props = timeline.getEventProperties(event);
			alert(props);
		};

		self.getDateTime = function(seconds) {
			var minutes = 0,
				hours = 0;
			if (seconds / 60 > 0) {
				minutes = parseInt(seconds / 60, 10);
				seconds = seconds % 60;
			}
			if (minutes / 60 > 0) {
				hours = parseInt(minutes / 60, 10);
				minutes = minutes % 60;
			}
			return new Date(0, 0, 0, hours, minutes, seconds);
		};

		$rootScope.$on('updateTimeline', function(event, locname, startT, endT, group, labelTerm, shotId, shotNum) {
			if (locname != '') var locn = locname;
			else var locn = labelTerm;
			var startTime = self.getDateTime(startT);
			var endTime = self.getDateTime(endT);
			self.videoTimeline.data.rows.push({c: [
				  {v: group},
				  {v: locn},
				  {v: startTime},
				  {v: endTime}
			]});
			var ann = {
					group: group,
					name: locn,
					shotid: shotId,
					shotNum: shotNum,
					startT: startT,
					endT: endT
				};						
			self.annotations.push(ann);
		});

		$rootScope.$on('updateSubtitles', function() {

			/*for (var elems in self.videoTimeline.data.rows)
			{
				for (var line in elems.c)
				{
					alert(line[1]);
				}
			}*/

		});

	}

	function MapController($scope, $rootScope, NgMap, NavigatorGeolocation, GeoCoder, $timeout, sharedProperties) {

		var vm = this;
		vm.videolat = null;
		vm.videolng = null;
		vm.locname = null;
		vm.zoom = 15;
		vm.markers = [];

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

				map.addListener('zoom_changed', function() {
					var mapZ = map.getZoom();
					/*if (mapZ >= 16){
						for (var i=0; i<=vm.markers.length;i++)
						{
							//vm.markerStyle={'width': '500px','height': '500px'};
							    //change the size of the icon
							    vm.markers[i].icon.scaledSize = new google.maps.Size(440, 340);
						}
					}*/
				});

			});
		}, 3000);

		vm.openInfoWindow = function(e, selectedMarker) {
			e.preventDefault();
			google.maps.event.trigger(selectedMarker, 'click');
		};

		vm.googleMapsUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI&sensor=false&callback=initializeMap&libraries=places";

		$rootScope.$on('updateMap', function(event, locname, lat, lng, group, labelTerm, shotId, startT) {

			// force map resize
			$timeout(function() {
				NgMap.getMap({
					id: 'videomap'
				}).then(function(map) {

					var LatLng = {
						lat: lat,
						lng: lng
					};
					var photoRef = sharedProperties.getPhotoRef();

					var infoWindow = new google.maps.InfoWindow();

					if (photoRef === '') {
						var marker = new google.maps.Marker({
							map: map,
							position: new google.maps.LatLng(lat, lng),
							title: locname,
							options: {
								icon: {
									url: "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png"
								}
							}
						});
					} else {
						var marker = new google.maps.Marker({
							map: map,
							position: new google.maps.LatLng(lat, lng),
							title: locname,
							//icon: photoRef
							options: {
								icon: {
									url: photoRef,
									scaledSize: new google.maps.Size(44, 34)
								}
							}

						});
					}
					//marker.content = '<div class="infoWindowContent">' + locname + '</div>';
					var content = 'Location: ' + locname + ', Shot Id: ' + shotId;

					/*google.maps.event.addListener(marker, 'click', function(){
					    infoWindow.setContent('<h2>' + marker.title + '</h2><p>Shot id: '+shotId+'</p><p>' + marker.content + '</p>');
					    infoWindow.open($scope.map, marker);
					});*/
					google.maps.event.addListener(marker, 'click', function() {
						// close window if not undefined
						if (infoWindow !== void 0) {
							infoWindow.close();
						}
						// create new window
						var infoWindowOptions = {
							content: content
						};
						infoWindow = new google.maps.InfoWindow(infoWindowOptions);
						infoWindow.open(map, marker);
						self.jumpToShot(shotId, startT);
					});

					vm.markers.push(marker);

				});
			}, 1000);

			self.jumpToShot = function(selectedShot, startT) {
				// play video from selected shot
				var myVid = angular.element(window.document.querySelector('#videoarea'));
				myVid[0].currentTime = parseInt(startT);
				myVid[0].play();
			};

		});
	}

	// Please note that $modalInstance represents a modal window (instance) dependency.
	// It is not the same as the $uibModal service used above.
	function geoTagController($scope, $rootScope, $uibModalInstance, myGeoConfirmFactory, GeoCoder, DataService, sharedProperties) {
		$scope.geocodingResult = "";
		$scope.startT = sharedProperties.getStartTime();
		$scope.endT = sharedProperties.getEndTime();
		$scope.group = sharedProperties.getGroup();
		$scope.labelTerm = sharedProperties.getLabelTerm();
		$scope.shotPNGImage = sharedProperties.getShotPNG();
		$scope.IRI = sharedProperties.getIRI();
		$scope.shotID = sharedProperties.getShotId();
		$scope.shotNum = sharedProperties.getShotNum();

		$scope.ok = function() {

			if (!angular.isUndefined($scope.vm)) {

				var route = '';
				var locality = '';
				var country = '';

				if ($scope.vm.address.route != null) var route = $scope.vm.address.route;
				if ($scope.vm.address.locality != null) var locality = $scope.vm.address.locality;
				if ($scope.vm.address.country != null) var country = $scope.vm.address.country;
				if ($scope.vm.address.photo_reference != null) var photo_reference = $scope.vm.address.photo_reference;

				var stringloc = route + ' ' + locality + ' ' + country;

				GeoCoder.geocode({
						address: stringloc
					})
					.then(function(result) {
						var locationlat = result[0].geometry.location.lat();
						var locationlng = result[0].geometry.location.lng();
						var locationiri = result[0].place_id;
						sharedProperties.setLat(locationlat);
						sharedProperties.setLong(locationlng);
						sharedProperties.setIRI(locationiri); //actually the google one
						sharedProperties.setPhotoRef(photo_reference);
						var locname = result[0].formatted_address; //result[0].address_components[0].long_name;
						sharedProperties.setFormAddr(locname);
						var restring = '(lat, lng) ' + locationlat + ', ' + locationlng + ' (address: \'' + locname + '\')';
						myGeoConfirmFactory.open('lg', 'result.html', {
							result: restring,
							resarr: result
						});

						$uibModalInstance.close($scope.vm.address.locality);
					});
				//$uibModalInstance.close($scope.searchTerm);
			} else {
				var vid = sharedProperties.getVideoId();
				$scope.alternatives = sharedProperties.getAlternatives();
				var target = 'shot:' + $scope.shotID;
				//alternatives mechanism should be of course generalized

				if ($scope.labelTerm !== "") {
					var source = {
						"iri": $scope.IRI,
						"name": $scope.labelTerm,
						"alternativeNames": {
							"de": $scope.alternatives.de,
							"en": $scope.alternatives.en
						}
					};
					//save the annotation into the database
					//DataService.saveAnnotation(target, source);

					$rootScope.$emit('updateTimeline', '', $scope.startT, $scope.endT, $scope.group, $scope.labelTerm, $scope.shotID, $scope.shotNum);
				}
				$uibModalInstance.close(null);

			}
		};

		$scope.cancel = function() {
			$uibModalInstance.dismiss('cancel');
		};

	}

	function geoResultController($scope, $rootScope, $document, $uibModalInstance, params, sharedProperties, DataService) {
		$scope.geocodingResult = params.result;
		$scope.geoResArray = params.resarr;

		$scope.ok = function() {
			var res = $scope.geocodingResult;
			var rarr = $scope.geoResArray;

			$scope.startT = sharedProperties.getStartTime();
			$scope.endT = sharedProperties.getEndTime();
			$scope.group = sharedProperties.getGroup();
			$scope.labelTerm = sharedProperties.getLabelTerm();
			$scope.shotID = sharedProperties.getShotId();
			$scope.shotNum = sharedProperties.getShotNum();
			$scope.IRI = sharedProperties.getIRI();
			// $scope.alternatives = sharedProperties.getAlternatives();
			$scope.latitude = sharedProperties.getLatitude();
			$scope.longitude = sharedProperties.getLongitude();
			$scope.format = sharedProperties.getFormAddr();

			var target = 'shot:' + $scope.shotID;
			// alternatives mechanism should be of course generalized
			console.log($scope.IRI);
			console.log(res);
			console.log(rarr);
			var source = {
				// "iri": $scope.IRI,
				"iri": $scope.IRI,
				"name": $scope.labelTerm,
				// "alternativeNames": {
				// 	"de": $scope.alternatives.de,
				// 	"en": $scope.alternatives.en
				// },
				"spatial": {
					"lat": $scope.latitude,
					"long": $scope.longitude
				}
			};
			//save the annotation into the database
			//DataService.saveAnnotation(target, source);

			var foundterm = false;
			foundterm = $rootScope.checkAnnotation($scope.startT, $scope.endT, $scope.group, $scope.format);

			if (!foundterm) { //the annotation has not been found
				$rootScope.$emit('updateTimeline', $scope.format, $scope.startT, $scope.endT, $scope.group, $scope.labelTerm, $scope.shotID, $scope.shotNum);
				$rootScope.$emit('updateMap', $scope.format, $scope.latitude, $scope.longitude, $scope.group, $scope.labelTerm, $scope.shotID, $scope.startT);
			}

			$uibModalInstance.close($scope.geocodingResult);
		};

		$scope.cancel = function() {
			$uibModalInstance.dismiss('cancel');
		};

	}

})();