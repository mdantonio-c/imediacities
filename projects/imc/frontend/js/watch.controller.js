(function() {
	'use strict';

	var $ = require('jquery');
	var noteMaxLenght = 500;

	var app = angular.module('web')
		.controller('TagController', TagController)
		.controller('NotesController', NotesController)
		.controller('geoResultController', geoResultController)
		.controller('WatchController', WatchController)
		.controller('WatchImageController', WatchImageController)
		.controller('MapController', MapController)
		.controller('ModalConfirmController', ModalConfirmController);

	// modal view storyboard factory definition
	app.factory('modalFactory', modalFactory)
	   .factory('myTagModalFactory', myTagModalFactory)
	   .factory('myGeoConfirmFactory', myGeoConfirmFactory)
	   .factory('myNotesModalFactory', myNotesModalFactory);

	app.config(ivhTreeviewConf);
	app.service('sharedProperties', sharedProperties);

	function modalFactory($uibModal) {
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
	};
	modalFactory.$inject = ["$uibModal"];

	function myTagModalFactory($uibModal, $document) {
		/* modal view for adding location and term tags */
		return {
			open: function(size, template, params) {
				var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
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
	}
	myTagModalFactory.$inject = ["$uibModal", "$document"];

	function myGeoConfirmFactory($uibModal, $document) {
		/*var parentElem = angular.element($document[0].querySelector('#video-wrapper .tag-modal-parent'));*/
		var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
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
	};
	myGeoConfirmFactory.$inject = ["$uibModal", "$document"];

	function myNotesModalFactory($uibModal, $document) {
		/* modal view for adding notes */
		return {
			open: function(size, template, params) {
				var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
				return $uibModal.open({
					animation: true,
					templateUrl: template,
					controller: 'NotesController',
					controllerAs: '$notesCtrl',
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
	};
	myNotesModalFactory.$inject = ["$uibModal", "$document"];

	function ivhTreeviewConf(ivhTreeviewOptionsProvider) {
		ivhTreeviewOptionsProvider.set({
			defaultSelectedState: false,
			twistieExpandedTpl: '<i class="fa fa-minus-square-o imc-icon" aria-hidden="true"></i>',
			twistieCollapsedTpl: '<i class="fa fa-plus-square-o imc-icon" aria-hidden="true"></i>',
			twistieLeafTpl: '',
			validate: true
		});
	};
	ivhTreeviewConf.$inject = ["ivhTreeviewOptionsProvider"];

	function sharedProperties($q) {
		var startTime = 'test start value';
		var endTime = 'test end value';
		var labelTerm = 'test label value';
		var group = 'test group value';
		var shotPNG = 'test shot PNG value';
		var itemId = '';
		var videoId = '';
		var IRI = '';
		var shotId = '';
		var latitude = '';
		var longitude = '';
		var formatted = '';
		var photoref = '';
		var shotnum = '';
		var recordProvider, defer = $q.defer();

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
			getItemId: function() {
				return itemId;
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
			setItemId: function(value) {
				itemId = value;
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
			getRecordProvider: function() { 
				return defer.promise;
			},
			setRecordProvider: function(value) {
				recordProvider = value;
				defer.notify(recordProvider);
			}
		};
	};
	sharedProperties.$inject = ["$q"];

	function trustUrl($sce) {
		return function(url) {
			return $sce.trustAsResourceUrl(url);
		};
	};
	trustUrl.$inject = ["$sce"];

	app.filter('trustUrl', trustUrl)
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
		/* obj può essere direttamente il valore oppure può essere una struttura key,description */
		.filter('attributesFilter', function() {
			return function(obj) {
				if(obj && obj.description){
					return obj.description;
				}
				return obj;
			};
		})
		/* convert UTC date time in local date time and format it */
		.filter('localDateTime', function() {
			return function(utcDateTime) {
				//console.log("utcDateTime=" + utcDateTime);
				var localDateTime  = moment.utc(utcDateTime).toDate();
			    //console.log("localDateTime=" + localDateTime);
    			localDateTime = moment(localDateTime).format('YYYY-MM-DD HH:mm:ss');
			    //console.log("localDateTime=" + localDateTime);
    			return localDateTime;
			};
		})
		.filter('switchVideoType', function() {
			return function(link, ctype) {
				if (link === undefined) return;
				if (ctype === undefined) { ctype = 'video'; }
				var idx = link.lastIndexOf("?");
				if (idx != -1) {
					link = link.substr(0, idx) + '?type=' +ctype;
				}
				return link;
			};
		})
		;

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
					var startTime = convertToMilliseconds($elm[0].firstElementChild.attributes.timestamp.value);

					//var times = convertTime(startTime);

					var seekTime = ((Number(startTime) / 1000) + 0.001);
					$scope.videoplayer.time_goto(seekTime);
				    $scope.videoplayer.video.play();
				});
			}
		};
	});
	app.directive('scrollOnClick', function() {
		return {
			link: function(scope, $elm) {
				$elm.on('click', function() {
					//console.log('scroll on click');
					if ($elm[0].parentNode.className == "scrollmenu") {
						$(".scrollmenu").animate({
							scrollLeft: $elm[0].offsetLeft
						}, "slow");
					}
					// set the shot selected in notes tab
					var shotSelectedForNotes = parseInt($elm[0].attributes.progr.value) + 1;
					scope.$emit('updateShotSelectedForNotes', shotSelectedForNotes);
					// play video from selected shot
					var startTime = convertToMilliseconds($elm[0].attributes.timestamp.value);
					var seekTime = ((Number(startTime) / 1000) + 0.001);
					$scope.videoplayer.time_goto(seekTime);
				    $scope.videoplayer.video.play();
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
					result.viewport = [
						place.geometry.viewport.getNorthEast(),
						place.geometry.viewport.getSouthWest()
					];
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
		console.log(currtime);
		var hours = currtime.split(":")[0];
		var mins = currtime.split(":")[1];
		var secs = currtime.split(":")[2];
		var cdate = new Date(0, 0, 0, hours, mins, secs);
		var times = (secs * 1) + (mins * 60) + (hours * 3600); //convert to seconds

		return times;
	}

	/**
	 * Convert a shot timecode (e.g 00:00:50-f21) to seconds 
	 */
	function convertoToSeconds(timecode) {
		var time = timecode.split('-')[0].split(':');
		return (((Number(time[0]) * 60) * 60) + (Number(time[1]) * 60) + Number(time[2]));
	}

	/**
	 * Convert a shot timecode (e.g 00:00:50-f21) to milliseconds
	 */
	function convertToMilliseconds(timecode, framerate) {
		if (framerate === undefined) framerate = 24;
		var frames = Number(timecode.split('-')[1].substring(1, 3));
		var milliseconds = (1000 / framerate) * (isNaN(frames) ? 0 : frames);
		return Math.floor((convertoToSeconds(timecode) * 1000) + milliseconds);
	}

	/**
	 * Covert a Date object to milliseconds. Consider only the part HH:mm:ss.sss
	 */
	function convertDateToMilliseconds(time) {
		var hours = time.getHours();
		var minutes = time.getMinutes();
		var seconds = time.getSeconds();
		var milliseconds = time.getMilliseconds();
		return 1000 * (seconds + (minutes * 60) + (hours * 3600)) + milliseconds;
	}

	function WatchController(
		$scope, $rootScope, $interval, $http, $log, $document, $uibModal, 
		$stateParams, $filter, $timeout, DataService, noty, 
		myTagModalFactory, myNotesModalFactory, sharedProperties) {

		function encodeLanguage(language) {
			// TODO da completare 
			var code=null;
			if (language === 'English') { code = 'en'; }
			else if(language === 'Italian') { code = 'it'; }
			else if(language === 'Greek') { code = 'el'; }
			else if(language === 'Spanish') { code = 'es'; }
			else if(language === 'Dutch') { code = 'nl'; }
			else if(language === 'French') { code = 'fr'; }
			else if(language === 'Danish') { code = 'da'; }
			else if(language === 'German') { code = 'de'; }
			else if(language === 'Swedish') { code = 'sv'; }
			return code;
		}
		function decodeLanguageCode(code) {
			// TODO da completare 
			var language=null;
			if (code === 'en') { language = 'English'; }
			else if(code === 'it') { language = 'Italian'; }
			else if(code === 'el') { language = 'Greek'; }
			else if(code === 'es') { language = 'Spanish'; }
			else if(code === 'nl') { language = 'Dutch'; }
			else if(code === 'fr') { language = 'French'; }
			else if(code === 'da') { language = 'Danish'; }
			else if(code === 'de') { language = 'German'; }
			else if(code === 'sv') { language = 'Swedish'; }
			return language;
		}

		var self = this;
		var vid = $stateParams.v;
		self.showmeli = true;
		self.video = $stateParams.meta;
		//console.log("self.video="+angular.toJson(self.video));
		self.videoType = 'video';
		var intervalRewind;

/* 		// << NSI >> //
		setTimeout( function(){
			var v = new VideoPlayer({
			selector: '#disagio',
			sources: ["http://192.168.2.37:8080/api/videos/cbdebde9-0ccb-40d9-8dbe-bad3d201a3e5/content?type=video"],
			fps: 24,
		});
		}, 2000) */		

		$scope.rew = function() {
        // Don't start a new rewind if we are already doing it
        if ( angular.isDefined(intervalRewind) ) return;

		intervalRewind = $interval(function(){
       		myVid[0].playbackRate = 1.0;
       		if(myVid[0].currentTime == 0){
				$scope.stopBack();
           			myVid[0].pause();
      			}
       			else{
           			myVid[0].currentTime += -.1;
       			}
            },30);
        };

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

		// to visualize notes in notes tab 
		self.notes = [];
		// to visualize shots in notes tab table
		self.notesShots = [];
		// current shot in notes tab table
		self.notesShotSelected=1;

		// initialize multiselect to filter subtitles
		$scope.options = [];
		$scope.selectedOptions = [];

		// Initializing values
		self.onplaying = false;
		self.onpause = true;
		var paused = false; //warning, this is a one shot variable, we need it only once loading the search page
		self.showtagtxt = false;

		var myVid = angular.element($document[0].querySelector('#videoarea'));
		$rootScope.currentTime = myVid[0].currentTime;

		self.startTagTime = $rootScope.currentTime;
		self.currentvidDur = 0;

		// On video time update: update the selected shot on the Notes tab
		myVid[0].ontimeupdate = function() {
			/*
			//console.log('ontimeupdate start');
			var currentTime = parseInt(myVid[0].currentTime);
			// calculate the shot at current time
			var currentShotNotes = getShotFromVideoCurrentTime(currentTime);
			//console.log('current shot: ' + angular.toJson(currentShotNotes, true));
			$scope.$emit('updateShotSelectedForNotes', currentShotNotes);
			$scope.$digest(); //refresh scope  // serve in questo caso? SI
			//console.log('ontimeupdate end');
			*/
		};

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

		// On video error
		myVid[0].onerror = function(event) {
			let error = event;
			console.log(event);
			var currentSrc;
			// Chrome v60
		    if (event.path && event.path[0]) {
		      error = event.path[0].error;
		      currentSrc = event.path[0].currentSrc;
		    }

		    // Firefox v55
		    if (event.originalTarget) {
		      error = event.originalTarget.error;
		      currentSrc = event.originalTarget.currentSrc;
		    }

		    // Here comes the error message
		    noty.showError(`Video error: ${error.message}`);
		    if (currentSrc.endsWith('orf')) {
		    	self.switchVideo();
		    }
		};

		// Play video function
		function playVid(video) {
			// console.log('play video');
			$scope.stopBack();
			if (myVid[0].paused && !self.onplaying) {
				self.onpause = false;
				self.onplaying = true;
				video.currtime = '3';
				video.play();
			}
		}

		self.playPause = function() {
			// console.log('pause video');
			myVid[0].playbackRate = 1.0;
			$scope.stopBack();
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
		self.pauseVideo = function() {

			myVid[0].playbackRate = 1.0;
			$scope.stopBack();

			self.onpause = true;
			self.onplaying = false;
			myVid[0].pause();
		};

		self.switchVideo = function() {
			var video = $scope.videoplayer.video;
			var atTime = video.currentTime;
			video.pause();
			var currentSrc = $scope.videoplayer.conf.sources[0];
			if (self.videoType == 'video') {
				// stream video with detected objects
				self.videoType = 'orf';
			} else {
				// back to original video
				self.videoType = 'video';
			}
			// FIXME: changing source of the video player conf doesn't work
			$scope.videoplayer.conf.sources[0] = $filter('switchVideoType')(currentSrc, self.videoType);
			console.log('switch to content['+self.videoType+'] at time: '+ atTime);
			$timeout(function() {
				video.currentTime = atTime;
				video.play();
			}, 50);
		};

		self.manualtag = function(mode) {
			console.log('manual tag: ' + mode);

			// force the video to pause
			self.pauseVideo();
			// set the initial tag frame with current time
			self.startTagTime = Math.floor(myVid[0].currentTime * 1000);
			console.log('Stop video at time (ms): ' + self.startTagTime);

			for (var i = 0; i <= self.shots.length - 1; i++) {
				var shotThumbnail = self.shots[i].links.thumbnail;
				var shotId = self.shots[i].id;
				var shotNum = self.shots[i].attributes.shot_num;
				var shotTimestamp = self.shots[i].attributes.timestamp;
				var shotDuration = self.shots[i].attributes.duration;
				// console.log(shotNum + '\t' + shotTimestamp + '\t' + shotDuration);

				var shotStartTime = convertToMilliseconds(shotTimestamp);
				var nextStartTime = null;
				if (i < self.shots.length - 1) {
					// get start time from the next shot
					nextStartTime = convertToMilliseconds(self.shots[i+1].attributes.timestamp);
				} else {
					// last shot: use the shot duration instead
					nextStartTime = shotStartTime + (shotDuration * 1000);
				}
				if (self.startTagTime >= shotStartTime && self.startTagTime < nextStartTime) {
					//console.log('found shot number ' + (shotNum+1) + ', from start time ' + shotStartTime + ' (ms)');
					sharedProperties.setVideoId($stateParams.v);
					sharedProperties.setStartTime(shotStartTime);
					sharedProperties.setEndTime(nextStartTime);
					sharedProperties.setGroup(mode);
					sharedProperties.setShotPNG(shotThumbnail);
					sharedProperties.setShotId(shotId);
					sharedProperties.setShotNum(shotNum+1);

					// filter actual manual annotations for this shot
					var shot_annotations = $filter('filter')(self.annotations, {shotNum: shotNum+1});
					// console.log('actual annotations for this shot: '+ angular.toJson(shot_annotations, true));
					
					if (mode == 'term') {
						myTagModalFactory.open('lg', 'myModalVocab.html', {annotations: shot_annotations});
					}
					else if (mode == 'notes') {
						myNotesModalFactory.open('lg', 'myModalNotes.html', {annotations: shot_annotations});
					}
					else if (mode == 'location') {
						myTagModalFactory.open('lg', 'myModalGeoCode.html', {annotations: shot_annotations});
					}
					// exit loop
					break;
				}
			}
		};

		self.deleteAnnotation = function(anno) {
			//console.log("deleteAnnotation anno=" + angular.toJson(anno, true));
			var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
			var modalInstance = $uibModal.open({
				templateUrl: 'confirmModal.html',
				animation: false,
				size: 'sm',
				controller: 'ModalConfirmController',
				appendTo: parentElem
			});
			var annoId = anno.id;
			var bodyIRI = anno.iri;
			var bodyName = anno.name;
			var bodyRef = (anno.iri !== undefined) ? 'resource:' + bodyIRI : 'textual:' + bodyName;
			modalInstance.result.then(function() {
				// YES: delete annotation
				DataService.deleteAnnotation(annoId, bodyRef).then(function() {
					console.log('Annotation [' + annoId + ']['+ bodyRef +'] deleted successfully');
					angular.forEach(self.annotations, function(anno, index) {
						if (anno.id === annoId &&
							((anno.iri !== undefined && anno.iri === bodyIRI) ||
								anno.name === bodyName)) {
							self.annotations.splice(index, 1);
						}
					});
					// update the timeline with the remaining annotations
					$rootScope.$emit('updateTimeline', '', null, null);
				}, function(err) {
					// TODO
				});
			}, function() {
				// NO: do nothing
			});
		};
		self.deleteNote = function(note) {
			//console.log(angular.toJson(note, true));
			var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
			var modalInstance = $uibModal.open({
				templateUrl: 'confirmNoteModal.html',
				animation: false,
				size: 'sm',
				controller: 'ModalConfirmController',
				appendTo: parentElem
			});
			var noteId = note.id;
			modalInstance.result.then(function() {
				// YES: delete annotation
				DataService.deleteNote(noteId).then(function() {
					console.log('Note [' + noteId + '] deleted successfully');
					angular.forEach(self.notes, function(note, index) {
						if (note.id === noteId ) {
							self.notes.splice(index, 1);
						}
					});
					// update the notes tab with the remaining notes
					// Non c'e' bisogno viene aggiornata in automatico 
					//  perche' cambia la variabile self.notes
					//$rootScope.$emit('updateNotes', null, null);
				}, function(err) {
					// TODO
				});
			}, function() {
				// NO: do nothing
			});
		};
		self.editNote = function(note) {
			//console.log("editNote: note=" + angular.toJson(note, true));
			var shot_annotations = null;
			var shotInfo = self.shots[note.shotNum-1];
			myNotesModalFactory.open('lg', 'myModalNotes.html', {annotations: shot_annotations, note: note, shot: shotInfo});		
		};

		// ritorna le classi css da applicare agli elementi
		//  della lista degli shot nel tab delle note
		self.computeCssClass = function(last,shot) {
		    var cssClass = "tab-list-shot";
		    if(last){
		    	cssClass += " tab-list-shot-last";
		    }
		    if(shot == self.notesShotSelected){
		    	cssClass += " tab-list-shot-selected";
		    }else{
		    	cssClass += " tab-list-shot-no-selected";		    	
		    }
		    //console.log('computeCssClass=' + cssClass);
		    return cssClass;
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
					self.vduration = vduration;
					console.log('video duration: ' + vduration);
					//console.log('vid', vid);

					// timeline definition
					var minutes = 0,
						hours = 0,
						seconds = parseInt(vduration),
						milliseconds = (vduration % 1) * 1000;
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
								colorByRowLabel: true,
								tooltipDateFormat: format+'.SSS'
							},
							colors: ['#cbb69d', '#603913'],
							avoidOverlappingGridLines: false,
							hAxis: {
								minValue: new Date(0, 0, 0, 0, 0, 0, 0),
								maxValue: new Date(0, 0, 0, hours, minutes, seconds, milliseconds),
								format: format
							}
						}
					};
					//console.log('max timeline value: ' + moment(self.videoTimeline.options.hAxis.maxValue).format(format+'.SSS'));

					// add data to the timeline
					// cinzia: ho aggiunto lo shot num come ultima colonna
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

					// build items for the carousel and the storyboard
					var numberOfShots = self.shots.length;

					// << NSI >> //
					//	scenette
					var scene = [];
					//	durata e fps
					var durata = self.video.relationships.item[0].attributes.duration;
					var fps = self.video.relationships.item[0].attributes.framerate.replace('/1','');
					var flen = durata/fps;

					angular.forEach(self.shots, function(shot, idx) {
						// for the carousel
						var frameshot = [];
						frameshot[0] = shot.attributes.start_frame_idx;
						frameshot[1] = self.video.relationships.item[0].attributes.duration;
						frameshot[2] = shot.attributes.duration;
						frameshot[3] = numberOfShots;
						frameshot[4] = idx;
						frameshot[5] = shot.attributes.timestamp;
						frameshot[6] = shot.links.thumbnail;
						frameshot[7] = shot.id;
						self.items.push(frameshot);

						// for the storyboard
						var framerange = shot.attributes.start_frame_idx + ' - ' + (shot.attributes.end_frame_idx - 1);
						var sbFields = {
							number: shot.attributes.shot_num + 1,
							timestamp: shot.attributes.timestamp,
							duration: parseInt(shot.attributes.duration),
							thumb: shot.links.thumbnail,
							framerange: framerange
						};

						// shot info for the timeline
						var shotStartTime = convertToMilliseconds(shot.attributes.timestamp);
						var shortEndTime = shotStartTime + (shot.attributes.duration * 1000);
						var shotInfo = {
							id: shot.id,
							shotNum: shot.attributes.shot_num + 1,
							startT: shotStartTime,
							endT: shortEndTime
						};
						
						// loop annotations
						for (var i = 0; i < shot.annotations.length; i++) {

							// << NSI >> //
							var scena = {
								id: shot.attributes.end_frame_idx,
								title: shot.attributes.start_frame_idx,
								start: shot.attributes.start_frame_idx/fps,
								end: shot.attributes.end_frame_idx/fps,
								thumbnail: shot.links.thumbnail
							};

							//	creo scene
							scene.push(scena);

							var anno = shot.annotations[i];
							//console.log("anno=" + angular.toJson(anno, true));
							if (anno.attributes.annotation_type.key === 'VIM') {
								// add camera motion attributes
								sbFields.camera = anno.bodies[0].attributes;
								continue;
							} else if (anno.attributes.annotation_type.key === 'TAG') {
								//console.log('annotation dal db=' + angular.toJson(anno));
								for (var j=0; j < anno.bodies.length; j++) {
									// annotation info
									var spatial = anno.bodies[j].attributes.spatial;
									var group = (spatial !== null && typeof spatial === 'object') ? 'location' : 'term';
									var name = (anno.bodies[j].type === 'textualbody') ? 
										anno.bodies[j].attributes.value : anno.bodies[j].attributes.name;
									var termIRI = anno.bodies[j].attributes.iri;
									var user_creator = anno.creator.id;
									var annoInfo = {
										id: anno.id,
										name: name,
										iri: termIRI,
										group: group,
										creator: user_creator
									};
									$rootScope.$emit('updateTimeline', '', annoInfo, shotInfo);
								}
							}else if (anno.attributes.annotation_type.key === 'DSC') { // note
								//console.log('nota dal db=' + angular.toJson(anno));
								// mi aspetto che la note abbia un solo body di tipo textual
								// il backend mi manda solo quelle che posso vedere
								var text = anno.bodies[0].attributes.value;
								var textLanguageCode = anno.bodies[0].attributes.language;
								//console.log('textLanguageCode=' + angular.toJson(textLanguageCode));
								var textLanguage = decodeLanguageCode(textLanguageCode);
								//console.log('textLanguage=' + angular.toJson(textLanguage));
								var creatorId = anno.creator.id;
								var creatorName = anno.creator.attributes.name + " " + anno.creator.attributes.surname;
								var privacy = "private";
								var creation_datetime = anno.attributes.creation_datetime;
								//console.log('anno.attributes.private=' + angular.toJson(anno.attributes.private));
								if(!anno.attributes.private){
									privacy = "public";
								}
								var noteInfo = {
									id: anno.id,
									text: text,
									textLanguage: textLanguage,
									textLanguageCode: textLanguageCode,
									creation_datetime: creation_datetime,
									creator: creatorId,
									creatorName: creatorName,
									privacy: privacy
								};
								//console.log('nota=' + angular.toJson(noteInfo));
								$rootScope.$emit('updateNotes', noteInfo, shotInfo);

							}else{
								console.log('not handled annotation type = '+anno.attributes.annotation_type.key);
							}

						}
						self.storyshots.push(sbFields);
						
					});

					// noteShots serve per il tab Notes a destra
					self.notesShots = self.storyshots;

					// << NSI >> //
					//	e se il video lo caricassi qui??
					$scope.videoplayer = new VideoPlayer({
						selector: '#videotest',
						sources: [self.video.links.content],
						fps: self.video.relationships.item[0].attributes.framerate.replace('/1',''),
						scene: scene
					});
  					// hide loading video bar
					self.showmeli = false;
				});
		};

		/**
		 * When the user selects a shot in the Notes Tab then
		 *  the tab must displays the notes of the selected shot
		 * @param selectedShotNum
		 */
		self.viewNotesOfSelectedShot = function(selectedShotNum) {
			//console.log('selectedShotNum=' + selectedShotNum);			
			self.notesShotSelected = selectedShotNum;
		};

		self.loadMetadataContent = function(vid) {
			// console.log("loading metadata content for vid: " + vid);
			self.loading = true;
			DataService.getVideoMetadata(vid).then(
				function(response) {
					self.video = response.data[0];
					self.currentvidDur = self.video.relationships.item[0].attributes.duration;
					self.isShownAt = self.video.relationships.record_sources[0].attributes.is_shown_at;
					sharedProperties.setRecordProvider(
						self.video.relationships.record_sources[0].relationships.provider[0].attributes.identifier);

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
			self.isShownAt = self.video.relationships.record_sources[0].attributes.is_shown_at;
			sharedProperties.setRecordProvider(
						self.video.relationships.record_sources[0].relationships.provider[0].attributes.identifier);
			self.loadVideoShots(vid, videoDuration);
		}

		self.selectedVideoId = vid;
		self.animationsEnabled = true;

		/**
		 * Jump to shot from the timeline.
		 * @param selectedShot - selected cell in the timeline with row and col.
		 */
		self.jumpToShot = function(selectedShot) {
			//console.log('jump to shot: selectedShot: ' + angular.toJson(selectedShot, true));
			var row = selectedShot.row;
			var startTime = convertDateToMilliseconds(
				self.videoTimeline.data.rows[row].c[2].v);
			// console.log('jump to shot: Start time: ' + startTime);
			// set the shot selected in notes tab
			var shotSelectedForNotes = self.videoTimeline.data.rows[row].c[4].v;
			//console.log('jump to shot: selectedShot: ' + angular.toJson(shotSelectedForNotes, true));
			$scope.$emit('updateShotSelectedForNotes', shotSelectedForNotes);
			// play video from selected shot
			var seekTime = ((Number(startTime) / 1000) + 0.001);
			$scope.videoplayer.time_goto(seekTime);
			$scope.videoplayer.video.play();
		};

		/**
		 * Jump to shot from the Annotation Tab.
		 * @param startTime - start time in milliseconds.
		 */
		self.jumpToShotFromAnnotation = function(startTime,selectedShot) {
			// console.log('jump to shot from annotation. Start time: ' + startTime);
			//console.log('jump to shot from annotation. shot num: ' + selectedShot);

			// set the shot selected in notes tab
			var shotSelectedForNotes = selectedShot;
			$scope.$emit('updateShotSelectedForNotes', shotSelectedForNotes);

			// play video from selected shot
			var seekTime = ((Number(startTime) / 1000) + 0.001);
			$scope.videoplayer.time_goto(seekTime);
			$scope.videoplayer.video.play();
		};

		self.getTagMenu = function(event) {
			var props = timeline.getEventProperties(event);
			alert(props);
		};

		/*
		 * Convert time value in milliseconds to a Date object to be passed into the timeline.
		 * 
		 * @param timestamp - time value in milliseconds.
		 * Not needed from the view. Make it private for this controller at the moment.
		 */
		function timelineToDate(timestamp) {
			var minutes = 0,
				hours = 0,
				seconds = Math.floor(timestamp / 1000),
				milliseconds = timestamp % 1000;
			if (seconds / 60 > 0) {
				minutes = parseInt(seconds / 60, 10);
				seconds = seconds % 60;
			}
			if (minutes / 60 > 0) {
				hours = parseInt(minutes / 60, 10);
				minutes = minutes % 60;
			}
			return new Date(0, 0, 0, hours, minutes, seconds, milliseconds);
		}

		$rootScope.$on('updateTimeline', function(event, locname, annoInfo, shotInfo) {
			//console.log("start updateTimeline");
			//console.log("annoInfo=" +angular.toJson(annoInfo,true));
			//console.log("shotInfo=" +angular.toJson(shotInfo,true));
			var startTime, endTime;
			if (annoInfo === null) {
				// just refresh the timeline
				self.videoTimeline.data.rows = [];
				angular.forEach(self.annotations, function(anno){
					startTime = timelineToDate(anno.startT);
					endTime = timelineToDate(anno.endT);
					self.videoTimeline.data.rows.push({c: [
						  {v: anno.group},
						  {v: anno.name},
						  {v: startTime},
						  {v: endTime},
						  {v: anno.shotNum}
					]});
				});
				return;
			}
			var locn = (locname !== '') ? locname : annoInfo.name;
			startTime = timelineToDate(shotInfo.startT);
			endTime = timelineToDate(shotInfo.endT);
			self.videoTimeline.data.rows.push({c: [
				  {v: annoInfo.group},
				  {v: locn},
				  {v: startTime},
				  {v: endTime},
				  {v: shotInfo.shotNum}
			]});
			var anno = {
					id: annoInfo.id,
					group: annoInfo.group,
					iri: annoInfo.iri,
					name: locn,
					creator: annoInfo.creator,
					shotid: shotInfo.id,
					shotNum: shotInfo.shotNum,
					startT: shotInfo.startT,
					endT: shotInfo.endT
				};						
			self.annotations.push(anno);
		});
		$rootScope.$on('updateShotSelectedForNotes', function(event, newShotSelected) {
			if (newShotSelected === null) {
				return;
			}
			if(self.notesShotSelected != newShotSelected){
				//console.log("updateShotSelectedForNotes start: " + angular.toJson(newShotSelected, true));
				self.notesShotSelected = newShotSelected;
			}
			return;
		});		
		$rootScope.$on('updateNotes', function(event, noteInfo, shotInfo) {
			//console.log("updateNotes start: " + angular.toJson(noteInfo, true));
			if (noteInfo === null) {
				return;
			}
			// se la nota esiste gia' allora e' un update
			var noteId = noteInfo.id;
			var update = false;
			angular.forEach(self.notes, function(note, index) {
				if (note.id === noteId ) {
					self.notes[index].text = noteInfo.text;
					self.notes[index].privacy = noteInfo.privacy;
					self.notes[index].language = noteInfo.textLanguage;
					self.notes[index].languageCode = noteInfo.textLanguageCode;
					update = true;
				}
			});
			//console.log("updateNotes update=" + angular.toJson(update, true));
			if(!update){
				// add the new note to self.notes
				var note = {
					id: noteInfo.id,
					text: noteInfo.text,
					language: noteInfo.textLanguage,
					languageCode: noteInfo.textLanguageCode,
					creatorName: noteInfo.creatorName,
					creator: noteInfo.creator,
					creation_datetime: noteInfo.creation_datetime,
					privacy: noteInfo.privacy,
					shotId: shotInfo.id,
					shotNum: shotInfo.shotNum,
					shotStartT: shotInfo.startT,
					shotEndT: shotInfo.endT
				};				
				self.notes.push(note);
			}
			//console.log("situazione delle note: " + angular.toJson(self.notes, true));
			return;
		});
		$rootScope.$on('updateSubtitles', function() {
			self.filtered = [];				
			angular.forEach(self.annotations, function(anno) {
				if (($rootScope.currentTime >= anno.startT) && ($rootScope.currentTime <= anno.endT))
				{
					self.filtered.push(anno);
				}
			});
		});
	};

	WatchController.$inject = [
		"$scope", "$rootScope", "$interval", "$http", "$log", "$document", 
		"$uibModal", "$stateParams", "$filter", "$timeout", "DataService", "noty",
		"myTagModalFactory", "myNotesModalFactory", "sharedProperties"
	];

	function WatchImageController($scope, $rootScope, $http, $document, $uibModal, $stateParams, $filter,
			DataService, noty, myTagModalFactory, myNotesModalFactory, sharedProperties) {

		var self = this;
		var imageId = $stateParams.id;
		self.image = $stateParams.meta;
		//console.log("self.image="+angular.toJson(self.image));
		// inizialize address for automplete input tag for geolocation
		$scope.vm = {
			address: {}
		};
		// to visualize annotations in the tab 
		self.annotations = [];
		// to visualize notes in notes tab 
		self.notes = [];

		// initialize multiselect to filter subtitles
		$scope.options = [];
		$scope.selectedOptions = [];
		// items serve per la geolocalizzazione
		self.items = [];
		
		self.setIdentifyingTitle = function(data) {
			//console.log("setIdentifyingTitle");
			var identifyingTitle;
			if(data){
				// pick 'Original title' as identifying title
				for (var i = 0, len = data.relationships.titles; i < len; i++) {
					if (data.relationships.titles[i].attributes.relation.key === 'Original title') {
						identifyingTitle = data.relationships.titles[i].attributes.text;
						break;
					}
				}
				// if there is not 'Original title' then we get first title in the array
				if(!identifyingTitle){
					identifyingTitle = data.relationships.titles[0].attributes.text;
				}			
			}
			//console.log("identifyingTitle=" + identifyingTitle);
			return identifyingTitle;
		};

		self.loadImageAnnotations = function(imageId) {
			//console.log("loading annotations for imageId: " + imageId);
			self.loading = true;
			DataService.getImageAnnotations(imageId).then(
				function(response) {
					//console.log("get annotations response: " + angular.toJson(response));
					var annos = response.data;
					//console.log("annos: " + angular.toJson(annos));
					for (var i = 0; i < annos.length; i++) {
						if (annos[i].attributes.annotation_type.key === 'TAG') {
								//console.log('annotation dal db=' + angular.toJson(annos[i]));
								for (var j=0; j < annos[i].bodies.length; j++) {
									// annotation info
									var spatial = annos[i].bodies[j].attributes.spatial;
									var group = (spatial !== null && typeof spatial === 'object') ? 'location' : 'term';
									var name = (annos[i].bodies[j].type === 'textualbody') ? 
										annos[i].bodies[j].attributes.value : annos[i].bodies[j].attributes.name;
									var termIRI = annos[i].bodies[j].attributes.iri;
									var user_creator = annos[i].creator.id;
									var annoInfo = {
										id: annos[i].id,
										name: name,
										iri: termIRI,
										group: group,
										creator: user_creator
									};
									self.annotations.push(annoInfo);
								}
							}else if (annos[i].attributes.annotation_type.key === 'DSC') { // note
								//console.log('nota dal db=' + angular.toJson(annos[i]));
								// mi aspetto che la note abbia un solo body di tipo textual
								// il backend mi manda solo quelle che posso vedere
								var text = annos[i].bodies[0].attributes.value;
								var textLanguageCode = annos[i].bodies[0].attributes.language;
								//console.log('textLanguageCode=' + angular.toJson(textLanguageCode));
								var textLanguage = decodeLanguageCode(textLanguageCode);
								//console.log('textLanguage=' + angular.toJson(textLanguage));
								var creatorId = annos[i].creator.id;
								var creatorName = annos[i].creator.attributes.name + " " + annos[i].creator.attributes.surname;
								var privacy = "private";
								var creation_datetime = annos[i].attributes.creation_datetime;
								//console.log('annos[i].attributes.private=' + angular.toJson(annos[i].attributes.private));
								if(!annos[i].attributes.private){
									privacy = "public";
								}
								var note = {
									id: annos[i].id,
									text: text,
									language: textLanguage,
									languageCode: textLanguageCode,
									creation_datetime: creation_datetime,
									creator: creatorId,
									creatorName: creatorName,
									privacy: privacy
								};
								self.notes.push(note);
								//console.log('nota=' + angular.toJson(noteInfo));
							}else{
								console.log('not handled annotation type = '+annos[i].attributes.annotation_type.key);
							}
					}
				},
				function(error) {
					console.log("get annotations error: " + angular.toJson(error));
					self.loading = false;
					noty.extractErrors(error, noty.ERROR);
				});
		};

		self.manualtag = function(mode) {
			console.log('manual tag: ' + mode);
			sharedProperties.setGroup(mode);
			if (mode == 'term') {
				myTagModalFactory.open('lg', 'myModalVocab.html', {annotations: self.annotations});
			}
			else if (mode == 'notes') {
				myNotesModalFactory.open('lg', 'myModalNotes.html', {annotations: null});
			}
			else if (mode == 'location') {
				myTagModalFactory.open('lg', 'myModalGeoCode.html', {annotations: self.annotations});
			}
		};

		self.deleteAnnotation = function(anno) {
			//console.log("delete anno=" + angular.toJson(anno, true));
			var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
			var modalInstance = $uibModal.open({
				templateUrl: 'confirmModal.html',
				animation: false,
				size: 'sm',
				controller: 'ModalConfirmController',
				appendTo: parentElem
			});
			var annoId = anno.id;
			var bodyIRI = anno.iri;
			var bodyName = anno.name;
			var bodyRef = (anno.iri !== undefined) ? 'resource:' + bodyIRI : 'textual:' + bodyName;
			//console.log("bodyRef=" + angular.toJson(bodyRef, true));
			modalInstance.result.then(function() {
				// YES: delete annotation
				DataService.deleteAnnotation(annoId, bodyRef).then(function() {
					console.log('Annotation [' + annoId + ']['+ bodyRef +'] deleted successfully');
					angular.forEach(self.annotations, function(anno, index) {
						if (anno.id === annoId &&
							((anno.iri !== undefined && anno.iri === bodyIRI) ||
								anno.name === bodyName)) {
							self.annotations.splice(index, 1);
						}
					});
				}, function(err) {
					// TODO
				});
			}, function() {
				// NO: do nothing
			});
		};
		self.deleteNote = function(note) {
			//console.log("deleteNote: note=" + angular.toJson(note, true));
			var parentElem = angular.element($document[0].querySelector('#item-wrapper .tag-modal-parent'));
			var modalInstance = $uibModal.open({
				templateUrl: 'confirmNoteModal.html',
				animation: false,
				size: 'sm',
				controller: 'ModalConfirmController',
				appendTo: parentElem
			});
			var noteId = note.id;
			modalInstance.result.then(function() {
				// YES: delete annotation
				DataService.deleteNote(noteId).then(function() {
					console.log('Note [' + noteId + '] deleted successfully');
					angular.forEach(self.notes, function(note, index) {
						if (note.id === noteId ) {
							self.notes.splice(index, 1);
						}
					});
					// update the notes tab with the remaining notes
					// Non c'e' bisogno viene aggiornata in automatico 
					//  perche' cambia la variabile self.notes
					//$rootScope.$emit('updateNotes', null, null);
				}, function(err) {
					// TODO
				});
			}, function() {
				// NO: do nothing
			});
		};
		self.editNote = function(note) {
			//console.log("editNote: note=" + angular.toJson(note, true));
			var shot_annotations = null;
			var shotInfo = null;
			myNotesModalFactory.open('lg', 'myModalNotes.html', {annotations: shot_annotations, note: note, shot: shotInfo});
		};

		self.loadMetadataContent = function(imageId) {
			//console.log("loading metadata content for imageId: " + imageId);
			self.loading = true;
			DataService.getImageMetadata(imageId).then(
				function(response) {
					//console.log("get metadata response: " + angular.toJson(response));
					self.image = response.data[0];		
					if(self.image){
						self.isShownAt = self.image.relationships.record_sources[0].attributes.is_shown_at;
						self.identifyingTitle = self.setIdentifyingTitle(self.image);
						//console.log("self.identifyingTitle=" + self.identifyingTitle);
						sharedProperties.setRecordProvider(self.image.relationships.record_sources[0].relationships.provider[0].attributes.identifier);
						sharedProperties.setItemId(self.image.relationships.item[0].id);
					}
					setTimeout(function() {
						$scope.$apply(function() {
							self.loading = false;
							self.loadImageAnnotations(imageId);
						});
					}, 2000);
					noty.extractErrors(response, noty.WARNING);
				},
				function(error) {
					console.log("get metadata error: " + angular.toJson(error));
					self.loading = false;
					noty.extractErrors(error, noty.ERROR);
				});
		};

		if (!$stateParams.meta) {
			//console.log("stateParams.meta is null, imageId="+imageId);
			self.loadMetadataContent(imageId);
		} else {
			//console.log("stateParams.meta is not null: " + angular.toJson($stateParams.meta));		
			if(self.image){
				self.identifyingTitle = self.setIdentifyingTitle(self.image);
				//console.log("self.identifyingTitle=" + self.identifyingTitle);
				sharedProperties.setRecordProvider(self.image.relationships.record_sources[0].relationships.provider[0].attributes.identifier);
				sharedProperties.setItemId(self.image.relationships.item[0].id);
				self.isShownAt = self.image.relationships.record_sources[0].attributes.is_shown_at;
			}
			// leggo le annotazioni dal db
			self.loadImageAnnotations(imageId);
		}

		self.getTagMenu = function(event) {
		};
		$rootScope.$on('updateNotes', function(event, noteInfo, shotInfo) {
			//console.log("updateNotes start: " + angular.toJson(noteInfo, true));
			if (noteInfo === null) {
				return;
			}
			// se la nota esiste gia' allora e' un update
			var noteId = noteInfo.id;
			var update = false;
			angular.forEach(self.notes, function(note, index) {
				if (note.id === noteId ) {
					self.notes[index].text = noteInfo.text;
					self.notes[index].privacy = noteInfo.privacy;
					self.notes[index].language = noteInfo.textLanguage;
					self.notes[index].languageCode = noteInfo.textLanguageCode;
					update = true;
				}
			});
			//console.log("updateNotes update=" + angular.toJson(update, true));
			if(!update){
				// add the new note to self.notes
				var note = {
					id: noteInfo.id,
					text: noteInfo.text,
					language: noteInfo.textLanguage,
					languageCode: noteInfo.textLanguageCode,
					creatorName: noteInfo.creatorName,
					creator: noteInfo.creator,
					creation_datetime: noteInfo.creation_datetime,
					privacy: noteInfo.privacy
				};				
				self.notes.push(note);
			}
			//console.log("situazione delle note: " + angular.toJson(self.notes, true));
			return;
		});
		$rootScope.$on('createdNewAnnotation', function(event, locname, annoInfo) {
			//console.log("WatchImageController: on createdNewAnnotation: annoInfo=" +angular.toJson(annoInfo,true));
			if (annoInfo === null) {
				return;
			}
			var locn = (locname !== '') ? locname : annoInfo.name;
			var anno = {
					id: annoInfo.id,
					group: annoInfo.group,
					iri: annoInfo.iri,
					name: locn,
					creator: annoInfo.creator,
				};						
			self.annotations.push(anno);
		});

	};


	function MapController($scope, $rootScope, $window, NgMap, NavigatorGeolocation, GeoCoder, $timeout, sharedProperties, GOOGLE_API_KEY) {

		var vm = this;
		vm.googleMapsUrl = GOOGLE_API_KEY;
		vm.videolat = null;
		vm.videolng = null;
		vm.locname = null;
		vm.markers = [];
		//vm.mapLoading = $scope.$parent.watchCtrl.video === undefined ? true : false;
		vm.mapLoading = true;

		// default location
		vm.location = 'Strasburgo, FR';
		vm.zoom = 4;

		// load the map ONLY when the provider info is available
		sharedProperties.getRecordProvider().then(null, null, function(provider) {

			// look for existing custom location
			var customLocation;
			var coverage;

			if ($scope.$parent.watchCtrl.video) {
				if ($scope.$parent.watchCtrl.video.relationships.coverages) {
					coverage = $scope.$parent.watchCtrl.video.relationships.coverages[0];
				}
			}

			if (coverage !== undefined) {
				customLocation = coverage.attributes.spatial[0];
			}

			if (customLocation === undefined) {
				//console.log('provider: ' + provider);
				switch (provider) {
					case "CCB":
						vm.location = 'Bologna, Italy';
						vm.zoom = 15;
						break;
					case "CRB":
						vm.location = 'Brussels, Belgium';
						vm.zoom = 15;
						break;
					case "DFI":
						vm.location = 'Copenhagen, Denmark';
						vm.zoom = 15;
						break;
					case "DIF":
						vm.location = 'Frankfurt am Main, German';
						vm.zoom = 15;
						break;
					case "FDC":
						vm.location = 'Barcelona, Spain';
						vm.zoom = 15;
						break;
					case "MNC":
						vm.location = 'Turin, Italy';
						vm.zoom = 15;
						break;
					case "OFM":
						vm.location = 'Vienna, Austria';
						vm.zoom = 15;
						break;
					case "SFI":
						vm.location = 'Stockholm, Sweden';
						vm.zoom = 15;
						break;
					case "TTE":
						vm.location = 'Athens, Greece';
						vm.zoom = 15;
						break;
				}
			} else {
				vm.location = customLocation;
				vm.zoom = 15;
			}
			// console.log('location: ' + vm.location);
			vm.mapLoading = false;
		});

		/*vm.init = function(location) {
			console.log('location from init: ' + location);
			vm.location = location === undefined ? 'Strasburgo, FR' : location;
            vm.zoom = 4;
		};*/

		NgMap.getMap("videomap").then(function(map) {
			//console.log('get map for location: ' + vm.location);
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
		}, 2000);
		$window.scrollTo(0, 0);

		vm.openInfoWindow = function(e, selectedMarker) {
			e.preventDefault();
			google.maps.event.trigger(selectedMarker, 'click');
		};

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
				$scope.videoplayer.time_goto(startT/1000);
				$scope.videoplayer.video.play();
			};

		});
	};
	MapController.$inject = [
		"$scope", "$rootScope", "$window", "NgMap", "NavigatorGeolocation",
		"GeoCoder", "$timeout", "sharedProperties"
	];

	// Please note that $modalInstance represents a modal window (instance) dependency.
	// It is not the same as the $uibModal service used above.
	function TagController($scope, $rootScope, $uibModalInstance, $filter, ivhTreeviewMgr, 
		myGeoConfirmFactory, DataService, sharedProperties, VocabularyService, params) {

		var self = this;
		
		$scope.geocodingResult = "";

		$scope.group = sharedProperties.getGroup();
		$scope.labelTerm = sharedProperties.getLabelTerm();
		$scope.IRI = sharedProperties.getIRI();

		// video SHOT
		$scope.startT = sharedProperties.getStartTime();
		$scope.endT = sharedProperties.getEndTime();
		$scope.shotPNGImage = sharedProperties.getShotPNG();
		$scope.shotID = sharedProperties.getShotId();
		$scope.shotNum = sharedProperties.getShotNum();
		// image
		$scope.itemId = sharedProperties.getItemId();

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

		// itemType: IMAGE, VIDEO
		// targetType: ITEM, SHOT
		self.confirmVocabularyTerms = function(itemType,targetType) {
			//console.log('confirmVocabularyTerms: itemType=' + itemType);
			//console.log('confirmVocabularyTerms: targetType=' + targetType);
			//var vid = sharedProperties.getVideoId();
			var target;
			if(targetType == 'ITEM'){
				// al momento il caso item e' solo per le immagini
				target = 'item:' + $scope.itemId;
			}else{
				target = 'shot:' + $scope.shotID;
			}
			if (self.tags.length > 0) {
				// save the annotation into the database
				DataService.saveTagAnnotations(target, self.tags).then(
					function(resp) {
						//console.log("saveTagAnnotations: resp.data=" + angular.toJson(resp.data, true));
						var annoId = resp.data.id;
						var creatorId = resp.data.creator.id;
						console.log('Annotation saved successfully. ID: ' + annoId);
						for (var i=0; i < self.tags.length; i++) {
							var annoInfo = {
								"id": annoId,
								"name": self.tags[i].label,
								"iri": self.tags[i].iri,
								"group": $scope.group,
								"creator": creatorId
							};
							//console.log("annoInfo=" + angular.toJson(annoInfo, true));
							if(itemType == 'IMAGE'){
								$rootScope.$emit('createdNewAnnotation', '', annoInfo);
							}else {
								var shotInfo = {
								"id": $scope.shotID,
								"shotNum": $scope.shotNum,
								"startT": $scope.startT,
								"endT": $scope.endT
								};
								//console.log("shotInfo=" + angular.toJson(shotInfo, true));
								$rootScope.$emit('updateTimeline', '', annoInfo, shotInfo);
							}
						}
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
	// Please note that $modalInstance represents a modal window (instance) dependency.
	// It is not the same as the $uibModal service used above.
	function NotesController($scope, $rootScope, $uibModalInstance, $filter, DataService, sharedProperties, params) {
		var self = this;
		$scope.group = sharedProperties.getGroup();
		$scope.labelTerm = sharedProperties.getLabelTerm();
		$scope.IRI = sharedProperties.getIRI();
		// video SHOT
		$scope.startT = sharedProperties.getStartTime();
		$scope.endT = sharedProperties.getEndTime();
		$scope.shotPNGImage = sharedProperties.getShotPNG();
		$scope.shotID = sharedProperties.getShotId();
		$scope.shotNum = sharedProperties.getShotNum();
		// image
		$scope.itemId = sharedProperties.getItemId();
		$scope.modalTitle = "Add a note";
		
		// dati della nota nel form della modale
		self.form = {};
		// serve per la select nella modale
		// privacy = public or private
		self.form.privacy = {
			options:  ["private","public"],
			selected: "private"
		};
		// serve per la select nella modale
		//  al momento non usato
		self.form.type = {
			options:  ["text","bibliography","link"],
			selected: "text"
		};
		// serve per la select nella modale
		// TODO da dove prendo le lingue?
		self.form.language = {
			options:  ["Danish","Dutch","English","French","German","Greek","Italian","Spanish","Swedish"],
			selected: null
		};
		// textarea nella modale
		self.form.text = ""; // mandatory

		// the new note the user is creating
		self.note = {};

		// if params is not null then we are coming from the edit note
		//  so we have to set the modal input fields with the values of
		//  note the user is editing
		if(params && params.note){
			//console.log("params=" + angular.toJson(params, true));
			$scope.modalTitle = "Edit the existing note";
			self.note = params.note;
			if(params.note.privacy){
				self.form.privacy.selected = params.note.privacy;
			}
			if(params.note.language){
				self.form.language.selected = params.note.language;
			}
			if(params.note.text){
				self.form.text = params.note.text;
			}
			$scope.shotNum = params.note.shotNum;
			$scope.shotID = params.note.shotId;
			$scope.startT = params.note.shotStartT;
			$scope.endT = params.note.shotEndT;
			if(params.shot && params.shot.links && params.shot.links.thumbnail){
				$scope.shotPNGImage = params.shot.links.thumbnail;
			}
		}

		self.confirmNote = function(itemType,targetType) {
			var target;
			if(targetType == 'ITEM'){
				target = 'item:' + $scope.itemId;
			}else{
				target = 'shot:' + $scope.shotID;
			}
			if (self.form.text && self.form.text.length > 0) {
				// note text max lenght = noteMaxLenght
				self.note.text = self.form.text.substring(0, noteMaxLenght);
				self.note.language = self.form.language.selected;
				self.note.languageCode = encodeLanguage(self.form.language.selected);
				self.note.privacy = self.form.privacy.selected;
				//console.log("before saveNote: note=" + angular.toJson(self.note, true));
				// save/update the Note into the database
				DataService.saveNote(target, self.note).then(
					function(resp) {
						//console.log("after saveNote: resp.data=" + angular.toJson(resp.data, true));
						var noteInfo;
						var shotInfo;
						if(self.note.id){
							// updated existing note
							noteInfo = {
								"id": self.note.id,
								"text": self.note.text,
								"textLanguage": self.note.language,
								"textLanguageCode": self.note.languageCode,
								"privacy": self.note.privacy
							};
						}else{
							// created a new note
							var noteId = resp.data.id;
							var creatorId = resp.data.creator.id;
							var creatorName = resp.data.creator.attributes.name + " " + 
								resp.data.creator.attributes.surname;
							var creationDatetime = resp.data.attributes.creation_datetime;
							noteInfo = {
								"id": noteId,
								"text": self.note.text,
								"textLanguage": self.note.language,
								"textLanguageCode": self.note.languageCode,
								"creator": creatorId,
								"creatorName": creatorName,
								"creation_datetime": creationDatetime,
								"privacy": self.note.privacy
							};
							shotInfo= {
								"id": $scope.shotID,
								"shotNum": $scope.shotNum,
								"startT": $scope.startT,
								"endT": $scope.endT
							};
						}
						if(itemType == 'IMAGE'){
							$rootScope.$emit('updateNotes', noteInfo, null);
						}else{
							$rootScope.$emit('updateNotes', noteInfo, shotInfo);
						}
					},
					function(err) {
						// TODO
					});
			}
			$uibModalInstance.close(null);
		};		
		self.cancel = function() {
			$uibModalInstance.dismiss('cancel');
			self.form.privacy.selected = "private";
			self.form.language.selected=null;
			self.form.type.selected="text";
			self.form.text = "";
		};

		self.alerts = [];
		self.closeAlert = function(index) {
			self.alerts.splice(index, 1);
		};

	}
	function geoResultController($scope, $rootScope, $document, $uibModalInstance, params, sharedProperties, DataService) {
		$scope.geoResult = params.result;
		$scope.group = sharedProperties.getGroup();
		$scope.labelTerm = sharedProperties.getLabelTerm();
		$scope.IRI = sharedProperties.getIRI();
		$scope.latitude = sharedProperties.getLatitude();
		$scope.longitude = sharedProperties.getLongitude();
		$scope.format = sharedProperties.getFormAddr();

		// video SHOT
		$scope.startT = sharedProperties.getStartTime();
		$scope.endT = sharedProperties.getEndTime();
		$scope.shotPNGImage = sharedProperties.getShotPNG();
		$scope.shotID = sharedProperties.getShotId();
		$scope.shotNum = sharedProperties.getShotNum();
		// image
		$scope.itemId = sharedProperties.getItemId();

		$scope.ok = function(itemType,targetType) {
			//console.log('geoResultController:ok: itemType=' + itemType);
			//console.log('geoResultController:ok: targetType=' + targetType);
			var target;
			if(targetType == 'ITEM'){
				target = 'item:' + $scope.itemId;
			}else{
				target = 'shot:' + $scope.shotID;				
			}
			//console.log($scope.IRI);
			//console.log($scope.labelTerm);
			var source = {
				"iri": $scope.IRI,
				"name": $scope.labelTerm
			};
			var spatial = {
				"lat": $scope.latitude,
				"long": $scope.longitude
			};

			// save the annotation into the database
			DataService.saveGeoAnnotation(target, source, spatial).then(
				function(resp) {
					var annoId = resp.data.id;
					var creatorId = resp.data.creator.id;
					var termIRI = source.iri;
					console.log('Annotation saved successfully. ID: ' + annoId);
					var annoInfo = {
						"id": annoId,
						"name": $scope.labelTerm,
						"iri": termIRI,
						"group": $scope.group,
						"creator": creatorId
					};
					if(itemType == 'IMAGE'){
						$rootScope.$emit('createdNewAnnotation', '', annoInfo);
					}else{
						var shotInfo = {
							"id": $scope.shotID,
							"shotNum": $scope.shotNum,
							"startT": $scope.startT,
							"endT": $scope.endT
						};
						$rootScope.$emit('updateTimeline', '', annoInfo, shotInfo);
					}
					$rootScope.$emit('updateMap', $scope.format, $scope.latitude, $scope.longitude, $scope.group, $scope.labelTerm, $scope.shotID, $scope.startT);				

				},
				function(err){
					// TODO
				});

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

