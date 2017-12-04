(function() {
	'use strict';

	var app = angular.module('web')
		.controller('TagController', TagController)
		.controller('geoResultController', geoResultController)
		.controller('WatchController', WatchController)
		.controller('MapController', MapController)
		.controller('ModalConfirmController', ModalConfirmController);

	// modal view storyboard factory definition
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
	}).factory('myModalGeoFactory', function($uibModal, $document) { /*modal view add location tag definition*/
		var parentElem = angular.element($document[0].querySelector('#video-wrapper .modal-parent'));
		return {
			open: function(size, template, params) {
				return $uibModal.open({
					animation: true,
					templateUrl: template || 'myModalGeoCode.html',
					controller: 'TagController',
					controllerAs: '$tagCtrl',
					size: size,
					appendTo: parentElem,
					resolve: {
						params: function() {
							return params;
						}
					}
				});
			}
		};
	}).factory('myGeoConfirmFactory', function($uibModal, $document) {
		var parentElem = angular.element($document[0].querySelector('#video-wrapper .modal-parent'));
		return {
			open: function(size, template, params) {
				return $uibModal.open({
					animation: true,
					templateUrl: template || 'result.html',
					controller: 'geoResultController',
					controllerAs: '$geoCtrl',
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

	app.config(function(ivhTreeviewOptionsProvider) {
		ivhTreeviewOptionsProvider.set({
			defaultSelectedState: false,
			twistieExpandedTpl: '<i class="fa fa-minus-square-o imc-icon" aria-hidden="true"></i>',
			twistieCollapsedTpl: '<i class="fa fa-plus-square-o imc-icon" aria-hidden="true"></i>',
			twistieLeafTpl: '',
			validate: true
		});
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
		.filter('matchTerms', function() {
			return function(terms, query) {
				if (terms === undefined || terms.length === 0) {
					return [];
				}
				var filtered = [];
				var recursiveFilter = function(terms, query) {
					angular.forEach(terms, function(item) {
						if (!item.hasOwnProperty('children')) {
							if (item.label.startsWith(query.toLowerCase())) {
								// console.log(angular.toJson(item, true));
								filtered.push({iri: item.id, label: item.label});
							}
						} else {
							recursiveFilter(item.children, query);
						}
					});
				};
				recursiveFilter(terms, query);
				return filtered;
			};
		})
		;
			/*.filter('timefilter',[ function () {
				return function(items, ctime) {
				    var filtered = [];            

				    angular.forEach(items, function(item) {
			    		var startT = item.startT;
			    		var endT = item.endT;						    		
			        	if((ctime.currentTime >= startT) && (ctime.currentTime <= endT)){ 
			            	filtered.push(item);						        
			        	}
				    });
				    return filtered;
				};
		}]);*/


	app.directive('scrollStoryOnClick', function() {
		return {
			//restrict: 'A',
			link: function($scope, $elm) {
				$elm.on('click', function() {
					// console.log('scroll on click');
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
					// console.log('scroll on click');
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
					result.place_id = place.place_id;
					result.name = place.name;
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
									if (!place.geometry) {
										// User entered the name of a Place that was not suggested and
      									// pressed the Enter key, or the Place Details request failed.
      									return;
									}
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

	/*app.directive('multiselect',['$document', function($document){
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
	}]);*/

	/* Range Slider
	    Input with default values:
	    -min=0      // Min slider value
	    -max=100    // Max slider value
	    -step=1     // Steps

	    Output / Input model
	    -value-min    // Default value @min
	    -value-max    // Default value @max

	    example:
	    <slider-range min="0" max="100" step="5" value-min="scope.form.slider_value_min" value-max="scope.form.slider_value_max"></slider-range>
	*/
	app.directive('sliderRange', ['$document',function($document) {

	// Move slider handle and range line
	  var moveHandle = function(handle, elem, posX) {
	    $(elem).find('.handle.'+handle).css("left",posX +'%');
	  };
	  var moveRange = function(elem,posMin,posMax) {
	    $(elem).find('.range').css("left",posMin +'%');
	    $(elem).find('.range').css("width",posMax - posMin +'%');
	  };

	return {
	    template: '<div class="slider horizontal">'+
	                '<div class="range"></div>'+
	                '<a class="handle min" ng-mousedown="mouseDownMin($event)"></a>'+
	                '<a class="handle max" ng-mousedown="mouseDownMax($event)"></a>'+
	              '</div>',
	    replace: true,
	    restrict: 'E',
	    scope:{
	      valueMin:"=",
	      valueMax:"="
	    },
	    link: function postLink(scope, element, attrs) {
	        // Initilization
	        var dragging = false;
	        var startPointXMin = 0;
	        var startPointXMax = 0;
	        var xPosMin = 0;
	        var xPosMax = 0;
	        var settings = {
	                "min"   : (typeof(attrs.min) !== "undefined"  ? parseInt(attrs.min,10) : 0),
	                "max"   : (typeof(attrs.max) !== "undefined"  ? parseInt(attrs.max,10) : 100),
	                "step"  : (typeof(attrs.step) !== "undefined" ? parseInt(attrs.step,10) : 1)
	            };
	        if ( typeof(scope.valueMin) == "undefined" || scope.valueMin === '' ) 
	            scope.valueMin = settings.min;
	            
	        if ( typeof(scope.valueMax) == "undefined" || scope.valueMax === '' ) 
	            scope.valueMax = settings.max;
	            
	        // Track changes only from the outside of the directive
	        scope.$watch('valueMin', function() {
	          if (dragging) return;
	          xPosMin = ( scope.valueMin - settings.min ) / (settings.max - settings.min ) * 100;
	          if(xPosMin < 0) {
	              xPosMin = 0;
	          } else if(xPosMin > 100)  {
	              xPosMin = 100;
	          }
	          moveHandle("min",element,xPosMin);
	          moveRange(element,xPosMin,xPosMax);
	        });

	        scope.$watch('valueMax', function() {
	          if (dragging) return;
	          xPosMax = ( scope.valueMax - settings.min ) / (settings.max - settings.min ) * 100;
	          if(xPosMax < 0) {
	              xPosMax = 0;
	          } else if(xPosMax > 100)  {
	              xPosMax = 100;
	          }
	          moveHandle("max",element,xPosMax);
	          moveRange(element,xPosMin,xPosMax);
	        });

	        // Real action control is here
	        scope.mouseDownMin = function($event) {
	            dragging = true;
	            startPointXMin = $event.pageX;
	        
	            // Bind to full document, to make move easiery (not to lose focus on y axis)
	            $document.on('mousemove', function($event) {
	                if(!dragging) return;

	                //Calculate handle position
	                var moveDelta = $event.pageX - startPointXMin;

	                xPosMin = xPosMin + ( (moveDelta / element.outerWidth()) * 100 );
	                if(xPosMin < 0) {
	                    xPosMin = 0;
	                } else if(xPosMin > xPosMax) {
	                  xPosMin = xPosMax;
	                } else {
	                    // Prevent generating "lag" if moving outside window
	                    startPointXMin = $event.pageX;
	                }
	                scope.valueMin = Math.round((((settings.max - settings.min ) * (xPosMin / 100))+settings.min)/settings.step ) * settings.step;
	                scope.$apply();
	                
	                // Move the Handle
	                moveHandle("min", element,xPosMin);
	                moveRange(element,xPosMin,xPosMax);
	            });
	        $document.mouseup(function(){
	                dragging = false;
	                $document.unbind('mousemove');
	                $document.unbind('mousemove');
	            });
	        };

	        scope.mouseDownMax = function($event) {
	            dragging = true;
	            startPointXMax = $event.pageX;
	        
	            // Bind to full document, to make move easiery (not to lose focus on y axis)
	            $document.on('mousemove', function($event) {
	                if(!dragging) return;

	                //Calculate handle position
	                var moveDelta = $event.pageX - startPointXMax;

	                xPosMax = xPosMax + ( (moveDelta / element.outerWidth()) * 100 );
	                if(xPosMax > 100)  {
	                    xPosMax = 100;
	                } else if(xPosMax < xPosMin) {
	                  xPosMax = xPosMin;
	                } else {
	                    // Prevent generating "lag" if moving outside window
	                    startPointXMax = $event.pageX;
	                }
	                scope.valueMax = Math.round((((settings.max - settings.min ) * (xPosMax / 100))+settings.min)/settings.step ) * settings.step;
	                scope.$apply();
	                
	                // Move the Handle
	                moveHandle("max", element,xPosMax);
	                moveRange(element,xPosMin,xPosMax);
	            });

	            $document.mouseup(function(){
	                dragging = false;
	                $document.unbind('mousemove');
	                $document.unbind('mousemove');
	            });
	        };
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
	/* start cinzia*/
	/* obj può essere direttamente il valore oppure può essere una struttura key,description */
	angular.module('web').filter('attributesFilter', function() {
		return function(obj) {
			if(obj && obj.description){
				return obj.description;
			}
			return obj;
		};
	});
	/* end cinzia*/

	function WatchController($scope, $http, $rootScope, $log, $document, $uibModal, $stateParams, 
		$filter, DataService, noty, myModalGeoFactory, sharedProperties) {

		var self = this;
		self.showmesb = false;
		self.showmeli = true;
		var vid = $stateParams.v;
		self.video = $stateParams.meta;

		self.inputVocTerm = "";
		// inizialize status of video format accordion
		$scope.statusAccor = {
    		isOpen: false
  		};
		// inizialize address for automplete input tag for geolocation
		$scope.vm = {
			address: {}
		};
		// to visualize annotations in tab table
		self.annotations = [];
		$rootScope.currentTime = 0;

		// initialize multiselect to filter subtitles
		$scope.options = [];
		$scope.selectedOptions = [];
		self.locSubtitle = "";

		// Initializing values
		self.onplaying = false;
		self.onpause = true;
		var paused = false; //warning, this is a one shot variable, we need it only once loading the search page
		self.showtagtxt = false;

		var myVid = angular.element(window.document.querySelector('#videoarea'));

		$rootScope.currentTime = parseInt(myVid[0].currentTime); //initialize current time
		self.startTagTime = $rootScope.currentTime;
		self.currentvidDur = 0;

		// On video playing toggle values
		myVid[0].onplaying = function() {
			self.onplaying = true;
			self.onpause = false;
			$rootScope.currentTime = parseInt(myVid[0].currentTime); //always update current time
			$scope.$digest(); //refresh scope
			if (!paused) {
				myVid[0].pause();
				paused = true;
			}
			// updating subtitles
			if (self.videoTimeline !== null) $rootScope.$emit('updateSubtitles');
		};

		// On video pause toggle values
		myVid[0].onpause = function() {
			self.onplaying = false;
			self.onpause = true;
		};

		// Play video function
		function playVid(video) {
			// console.log('play video');
			if (myVid[0].paused && !self.onplaying) {
				self.onpause = false;
				self.onplaying = true;
				video.currtime = '3';
				video.play();
			}
		}

		self.playAndPause = function() {
			// console.log('pause video');
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

		// Pause video
		self.pauseVid = function() {
			self.onpause = true;
			self.onplaying = false;
			myVid[0].pause();
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

				// same interval of this annotation set
				if ((parseInt(times1) == time1c) && (parseInt(times2) == time2c)) {
					var acategory = timelinerows[k].c[0].v;
					var aterm = timelinerows[k].c[1].v;
					if ((acategory == group) && (aterm == labelterm)) {
						// the term has been already added in the timeline cache
						foundterm = true;
						if (group == 'location') myModalGeoFactory.open('lg', 'locationFoundModal.html');
						else myModalGeoFactory.open('lg', 'termFoundModal.html');
					}
				}
			}
			return foundterm;
		};

		self.manualtag = function(group, labelterm, tiri, alternatives) {
			// console.log('manual tag - group: ' + group + '; term: ' + labelterm + '; iri: ' + tiri + '; alternatives: ' + alternatives);
			// console.log('current annotations: ' + angular.toJson(self.annotations, true));

			// force pause
			self.pauseVid();

			self.startTagTime = parseInt(myVid[0].currentTime); //set initial tag frame current time

			for (var i = 0; i <= self.shots.length - 1; i++) {
				var shotThumbnail = self.shots[i].links.thumbnail;
				var shotId = self.shots[i].id;
				var shotNum = self.shots[i].attributes.shot_num;

				var time1 = self.shots[i].attributes.timestamp;
				var times2;
				if (i < self.shots.length - 1) {
					// get timestamp from next shot
					var time2 = self.shots[i + 1].attributes.timestamp;
					var currtime2 = time2.split("-")[0];
					var hours2 = currtime2.split(":")[0];
					var mins2 = currtime2.split(":")[1];
					var secs2 = currtime2.split(":")[2];
					//var cdate = new Date(0, 0, 0, hours, mins, secs);
					times2 = (secs2 * 1) + (mins2 * 60) + (hours2 * 3600); //convert to seconds
				} else {
					// last shot: use duration instead
					times2 = self.shots[i].attributes.duration;
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
					sharedProperties.setShotPNG(shotThumbnail);
					sharedProperties.setShotId(shotId);
					sharedProperties.setShotNum(shotNum+1);

					// filter actual manual annotations for this shot
					var shot_annotations = $filter('filter')(self.annotations, {shotNum: shotNum+1});
					//console.log('actual annotations for this shot: '+ angular.toJson(shot_annotations, true));
					
					if (group != 'location') {
						// a new term
						if (!$rootScope.checkAnnotation(times1, times2, group, labelterm)) {
							myModalGeoFactory.open('lg', 'myModalVocab.html', {annotations: shot_annotations});
						}
					}
					else if (group == 'location') myModalGeoFactory.open('lg', 'myModalGeoCode.html', {annotations: shot_annotations});
				}
			}
		};

		self.deleteAnnotation = function(annoId) {
			var parentElem = angular.element($document[0].querySelector('#video-wrapper .modal-parent'));
			var modalInstance = $uibModal.open({
				templateUrl: 'confirmModal.html',
				animation: false,
				size: 'sm',
				controller: 'ModalConfirmController',
				appendTo: parentElem
			});
			modalInstance.result.then(function() {
				// YES: delete annotation
				DataService.deleteAnnotation(annoId).then(function() {
					console.log('Annotation [' + annoId + '] deleted successfully');
					angular.forEach(self.annotations, function(anno, index){
						if(anno.id === annoId) {
							self.annotations.splice(index, 1);
						}
					});
					$rootScope.$emit('updateTimeline', '', null, null);
				}, function(err) {
					// TODO
				});
			}, function() {
				// NO: do nothing
			});
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

						// once we have all data and metadata the video start playing
						/*if (i === 0) {
							var myVid = angular.element(window.document.querySelector('#videoarea'));
							playVid(myVid[0]);
						}*/

						// timeline definition
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

						// configuration
						self.videoTimeline = {
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
						self.videoTimeline.data = {
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
					} // end loop for shots in the response

					// build storyboard
					angular.forEach(self.shots, function(shot) {
						if ((shot.attributes !== undefined) && (shot.attributes.start_frame_idx !== undefined)) {
							var framerange = shot.attributes.start_frame_idx + ' - ' + (shot.attributes.end_frame_idx - 1);
							var sbFields = {
								thumb: shot.links.thumbnail,
								number: shot.attributes.shot_num + 1,
								framerange: framerange,
								timestamp: shot.attributes.timestamp,
								duration: parseInt(shot.attributes.duration),
								camera: shot.annotations[0].attributes
							};
							// add camera motion attributes
							for (var i = 0; i < shot.annotations.length; i++){
								var anno = shot.annotations[i];
								if (anno.attributes.annotation_type.key === 'VIM') {
									sbFields.camera = anno.bodies[0].attributes;
									break;
								} else if (anno.attributes.annotation_type.key === 'TAG') {
									// annotation info
									var spatial = anno.bodies[0].attributes.spatial;
									var group = (spatial !== null && typeof spatial === 'object') ? 'location' : 'term';
									var name = (anno.bodies[0].type === 'textualbody') ? 
										anno.bodies[0].attributes.value : anno.bodies[0].attributes.name;
									var termIRI = anno.bodies[0].attributes.iri;
									var annoInfo = {
										uuid: anno.id,
										name: name,
										iri: termIRI,
										group: group
									};
									// shot info
									var startT = convertTime(shot.attributes.timestamp);
									var endT = startT + shot.attributes.duration;
									var shotInfo = {
										uuid: shot.id,
										shotNum: shot.attributes.shot_num + 1,
										startT: startT,
										endT: endT
									};
									$rootScope.$emit('updateTimeline', '', annoInfo, shotInfo);
								}
							}
							self.storyshots.push(sbFields);
						}
					});
				});
		};


		self.loadMetadataContent = function(vid) {
			// console.log("loading metadata content for vid: " + vid);
			self.loading = true;
			DataService.getVideoMetadata(vid).then(
				function(response) {
					self.video = response.data[0];
					self.currentvidDur = self.video.relationships.item[0].attributes.duration;

					setTimeout(function() {
						$scope.$apply(function() {
							self.loading = false;
							self.loadVideoShots(vid, self.currentvidDur);
						});
					}, 2000);
					noty.extractErrors(response, noty.WARNING);
				},
				function(error) {
					self.loading = false;
					noty.extractErrors(error, noty.ERROR);
				});
		};

		if (!$stateParams.meta) {
			self.loadMetadataContent(vid);
		} else {
			var videoDuration = $stateParams.meta.relationships.item[0].attributes.duration;
			self.loadVideoShots(vid, videoDuration);
		}

		self.selectedVideoId = vid;
		self.animationsEnabled = true;

		self.jumpToShot = function(selectedShot) {
			console.log('jump to shot');
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
			console.log('jump to shot from annotation. startT: ' + startT);
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

		$rootScope.$on('updateTimeline', function(event, locname, annoInfo, shotInfo) {
			var startTime, endTime;
			if (annoInfo === null) {
				// just refresh the timeline
				self.videoTimeline.data.rows = [];
				angular.forEach(self.annotations, function(anno){
					startTime = self.getDateTime(anno.startT);
					endTime = self.getDateTime(anno.endT);
					self.videoTimeline.data.rows.push({c: [
						  {v: anno.group},
						  {v: anno.name},
						  {v: startTime},
						  {v: endTime}
					]});
				});
				return;
			}
			var locn = (locname !== '') ? locname : annoInfo.name;
			startTime = self.getDateTime(shotInfo.startT);
			endTime = self.getDateTime(shotInfo.endT);
			self.videoTimeline.data.rows.push({c: [
				  {v: annoInfo.group},
				  {v: locn},
				  {v: startTime},
				  {v: endTime}
			]});
			var anno = {
					id: annoInfo.uuid,
					group: annoInfo.group,
					iri: annoInfo.iri,
					name: locn,
					shotid: shotInfo.uuid,
					shotNum: shotInfo.shotNum,
					startT: shotInfo.startT,
					endT: shotInfo.endT
				};						
			self.annotations.push(anno);
		});

		$rootScope.$on('updateSubtitles', function() {
			self.filtered = [];				
			angular.forEach(self.annotations, function(ann) {
				var startT = ann.startT;
				var endT = ann.endT;
				if (($rootScope.currentTime >= startT) && ($rootScope.currentTime <= endT))
				{
					self.filtered.push(ann);
				}
			});
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
	function TagController($scope, $rootScope, $uibModalInstance, $filter, ivhTreeviewMgr, 
		myGeoConfirmFactory, DataService, sharedProperties, VocabularyService, params) {

		var self = this;
		
		$scope.geocodingResult = "";
		$scope.startT = sharedProperties.getStartTime();
		$scope.endT = sharedProperties.getEndTime();
		$scope.group = sharedProperties.getGroup();
		$scope.labelTerm = sharedProperties.getLabelTerm();
		$scope.shotPNGImage = sharedProperties.getShotPNG();
		$scope.IRI = sharedProperties.getIRI();
		$scope.shotID = sharedProperties.getShotId();
		$scope.shotNum = sharedProperties.getShotNum();

		self.vocabulary = [];
		VocabularyService.loadTerms().then(function(data) {
			self.vocabulary = data;
		});

		self.tags = [];
		self.loadVocabularyTerms = function(query) {
			return $filter('matchTerms')(self.vocabulary, query);
		};

		// custom treeview tpl
		self.treeviewTpl = [
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

		self.toggleTerm = function(node) {
			if (node.selected) {
				// add tag
				self.tags.push({iri: node.id, label: node.label});
			} else {
				self.tags = _.reject(self.tags, function(el) { return el.label === node.label; });
			}
		};

		self.selectTreeviewNode = function(tag) {
			if (tag.iri !== undefined) {
				// console.log('select treeview by node id: ' + tag.iri);
				ivhTreeviewMgr.select(self.vocabulary, tag.iri);
			}
		};

		self.deselectTreeviewNode = function(tag) {
			if (tag.iri !== undefined) {
				// console.log('deselect treeview by node id: ' + tag.iri);
				ivhTreeviewMgr.deselect(self.vocabulary, tag.iri);
			}
		};

		self.confirmLocation = function() {
			if (angular.isUndefined($scope.vm)) {
				self.alerts.push({msg: 'Invalid place selection. Only values from a controlled list is allowed.'});
				return;
			}
			var matched = $filter('filter')(params.annotations, {iri: $scope.vm.address.place_id})[0];
			if (typeof matched !== "undefined") {
				self.alerts.push({msg: 'Invalid place selection. "' + $scope.vm.address.name + '" already selected.'});
				return;
			}
			// check deplication
			// console.log('vm : ' + angular.toJson($scope.vm, true));
			var locationlat = $scope.vm.address.lat;
			var locationlng = $scope.vm.address.lng;
			var locname = $scope.vm.address.name;
			var locaddr = $scope.vm.address.formattedAddress;
			sharedProperties.setLat($scope.vm.address.lat);
			sharedProperties.setLong($scope.vm.address.lng);
			sharedProperties.setIRI($scope.vm.address.place_id); // at the moment the google place id
			sharedProperties.setLabelTerm($scope.vm.address.name);
			sharedProperties.setPhotoRef($scope.vm.address.photo_reference);
			sharedProperties.setFormAddr($scope.vm.address.formattedAddress);
			var restring = locname + ' (lat, lng) ' + locationlat + ', ' + locationlng + ' (address: \'' + locaddr + '\')';
			$uibModalInstance.close($scope.vm.address.locality);
			myGeoConfirmFactory.open('lg', 'result.html', {
				result: restring
			});
		};

		self.confirmVocabularyTerms = function() {
			var vid = sharedProperties.getVideoId();
			// $scope.alternatives = sharedProperties.getAlternatives();
			var target = 'shot:' + $scope.shotID;
			// alternatives mechanism should be of course generalized

			if (self.tags.length > 0) {
				// save the annotation into the database
				DataService.saveTagAnnotations(target, self.tags).then(
					// FIXME manage multiple tags
					function(resp) {
						var annoId = resp.data;
						console.log('Annotation saved successfully. ID: ' + annoId);
						var annoInfo = {
							"uuid": annoId,
							"name": self.tags[0].label,
							"iri": self.tags[0].iri,
							"group": $scope.group
						};
						var shotInfo = {
							"uuid": $scope.shotID,
							"shotNum": $scope.shotNum,
							"startT": $scope.startT,
							"endT": $scope.endT
						};
						$rootScope.$emit('updateTimeline', '', annoInfo, shotInfo);
					},
					function(err) {
						// TODO
					});
			}
			$uibModalInstance.close(null);
			ivhTreeviewMgr.deselectAll(self.vocabulary);
			ivhTreeviewMgr.collapseRecursive(self.vocabulary, self.vocabulary);
		};

		self.cancel = function() {
			$uibModalInstance.dismiss('cancel');
			ivhTreeviewMgr.deselectAll(self.vocabulary);
			ivhTreeviewMgr.collapseRecursive(self.vocabulary, self.vocabulary);
		};

		self.alerts = [];
		self.closeAlert = function(index) {
			self.alerts.splice(index, 1);
		};

	}

	function geoResultController($scope, $rootScope, $document, $uibModalInstance, params, sharedProperties, DataService) {

		$scope.geoResult = params.result;

		$scope.ok = function() {

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
			/*console.log($scope.IRI);
			console.log(res);
			console.log($scope.labelTerm);*/
			var source = {
				"iri": $scope.IRI,
				"name": $scope.labelTerm
			};
			var spatial = {
				"lat": $scope.latitude,
				"long": $scope.longitude
			};

			if (!$rootScope.checkAnnotation($scope.startT, $scope.endT, $scope.group, $scope.format)) { 
				// the annotation has not been found
				// save the annotation into the database
				DataService.saveGeoAnnotation(target, source, spatial).then(
						function(resp) {
							var annoId = resp.data;
							var termIRI = source.iri;
							console.log('Annotation saved successfully. ID: ' + annoId);
							var annoInfo = {
								"uuid": annoId,
								"name": $scope.labelTerm,
								"iri": termIRI,
								"group": $scope.group
							};
							var shotInfo = {
								"uuid": $scope.shotID,
								"shotNum": $scope.shotNum,
								"startT": $scope.startT,
								"endT": $scope.endT
							};
							$rootScope.$emit('updateTimeline', '', annoInfo, shotInfo);
							$rootScope.$emit('updateMap', $scope.format, $scope.latitude, $scope.longitude, $scope.group, $scope.labelTerm, $scope.shotID, $scope.startT);
						},
						function(err){
							// TODO
						});
			}

			$uibModalInstance.close($scope.geoResult);
		};

		$scope.cancel = function() {
			$uibModalInstance.dismiss('cancel');
		};

	}

	function ModalConfirmController($scope, $uibModalInstance) {
		$scope.yes = function() {
			$uibModalInstance.close();
		};

		$scope.no = function() {
			$uibModalInstance.dismiss('cancel');
		};
	}

})();