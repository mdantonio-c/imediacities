			(function() {
				'use strict';

				var app = angular.module('web')
					.controller('geoTagController', geoTagController)
					.controller('geoResultController', geoResultController)
					.controller('SearchController', SearchController)
					.controller('WatchController', WatchController)
					.controller('MapController', MapController)
					.controller('ModalResultInstanceCtrl', ModalResultInstanceCtrl)
					.controller('ModalInstanceCtrl', ModalInstanceCtrl);

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
				}).factory('myModalGeoFactory', function($uibModal) {
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
		  		})

		  		app.service('sharedProperties', function() {
	    		var startTime = 'test start value';
	    		var endTime = 'test end value';
	    	    var labelTerm = 'test label value';
	    	    var group = 'test label value';

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
	        		getGroup: function() {
	            		return group;
	        		},
	        		setStartTime: function(value) {
	            		startTime = value;
	        		},
	        		setEndTime: function(value) {
	            		endTime = value;
	        		},
	        		setLabelTerm: function(value) {
	            		labelTerm = value;
	        		},
	        		setGroup: function(value) {
	            		group = value;
	        		}
	    		}
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

				/*app.directive('scrollOnClick', function() {
						return {
							//restrict: 'A',
							link: function($scope, $elm) {
								$elm.on('click', function() {
								    if ($elm[0].parentNode.className == "scrollmenu"){
									$(".scrollmenu").animate({
										scrollLeft: ($elm[0].offsetLeft-($elm[0].parentNode.parentNode.scrollWidth/2))
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
					})*/
					app.directive('scrollOnClick', function() { //carousel version
						return {
							//restrict: 'A',
							link: function($scope, $elm) {
								$elm.on('click', function() {
									//alert($elm[0].parentNode.className);
									if ($elm[0].parentNode.className == "scrollmenu"){
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
									myVid[0].currentTime = times+5;
									myVid[0].play();

								});
							}
						};
					})
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
					]);


					app.directive('dropdown', function($document) {
					return {
						restrict: "C",
						link: function(scope, elem, attr) {
			
						elem.bind('click', function() {
						elem.toggleClass('dropdown-active');
						elem.addClass('active-recent');
						});
			
					$document.bind('click', function() {
						if(!elem.hasClass('active-recent')) {
						elem.removeClass('dropdown-active');
					}
					elem.removeClass('active-recent');
					});
			
					}
				}
				});

				function getElement(event) {
					return angular.element(event.srcElement || event.target);
				}

				function convertTime(currtime){

					currtime = currtime.split("-")[0];
					var hours = currtime.split(":")[0];
					var mins = currtime.split(":")[1];
					var secs = currtime.split(":")[2];
					var cdate = new Date(0, 0, 0, hours, mins, secs);
					var times = (secs * 1) + (mins * 60) + (hours * 3600); //convert to seconds

					return times;

				}

				// The controller
				function SearchController($scope, $log, $document, $state, $stateParams, DataService, noty, $uibModal) {
					var self = this;

					self.showmesb = false;
					self.viewlogo = true;
					self.showmese = false;
					//self.showmepg = true;

					/*Define options type for paginate page numbers*/
					self.typeOptions = [
			    		{ name: '4 per page', value: '4' }, 
			    		{ name: '8 per page', value: '8' }, 
			    		{ name: '15 per page', value: '15' }, 
			    		{ name: '20 per page', value: '20' }
			    	];

					//configure pagination
					self.ItemsByPage=self.typeOptions[0].value;
					self.currentPage=1;
					self.numvideos=0;

				 	self.bigTotalItems = 0;

					self.videos = [];

					self.loading = false;
					self.inputTerm = "";
					self.searchVideos = function() {
						var request_data = {
							"type": "video",
							"term": "",
							"numpage": 1,
							"pageblock": self.ItemsByPage
						};
						request_data.term = self.inputTerm === '' ? '*' : self.inputTerm;
						request_data.numpage = self.currentPage;
						request_data.pageblock = self.ItemsByPage;
						// console.log('search videos with term: ' + request_data.term);
						self.loadResults = false;
						self.loading = true;
						self.showmese = true;
						DataService.searchVideos(request_data).then(
							function(out_data) {
								self.numvideos = parseInt(out_data.data[out_data.data.length-1][0][0]);
								self.bigTotalItems = self.numvideos;
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

			    $scope.setPage = function () {
			        self.currentPage = this.n;
			        self.searchVideos();
			    };

			    $scope.firstPage = function () {
			        self.currentPage = 1;
			        self.searchVideos();
			    };

			    $scope.lastPage = function () {
			        self.currentPage = parseInt(self.numvideos/self.ItemsByPage) + 1;
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


			    $scope.range = function (input, total) {
			        var ret = [];
			        if (!total) {
			            total = input;
			            input = 0;
			        }
			        for (var i = input; i < total; i++) {
			            if (i != 0 && i != total - 1) {
			                ret.push(i);
			            }
			        }
			        return ret;
			    };

				}

				function WatchController($scope, $http, $rootScope, $log, $document, $uibModal, $stateParams, DataService, noty, myModalGeoFactory, sharedProperties) {

						var self = this;
						self.showmesb = false;
						self.showmeli = true;
						var vid = $stateParams.v;
						self.video = $stateParams.meta;

						self.vocabulary = [
					    {
					        "name": "Electronics",
					        "subHeader": [
					            {
					                "name": "Mobiles",
					                "view": "#mobile"
					            },
					            {
					                "name": "Tablet",
					                "view": "#tablet"
					            },
					            {
					                "name": "Television",
					                "view": "#television"
					            },
					            {
					                "name": "Headphones",
					                "view": "#headphones"
					            }
					        ]
					    },
					    {
					        "name": "Men",
					        "subHeader": [
					            {
					                "name": "Shirts",
					                "view": "#shirts"
					            },
					            {
					                "name": "T-shirts",
					                "view": "#tshirts"
					            },
					            {
					                "name": "Trousers",
					                "view": "#trousers"
					            },
					            {
					                "name": "Jeans",
					                "view": "#jeans"
					            }
					        ]
					    }
					];

					self.vocabularyFinal = $http.get('static/assets/vocabulary/vocabulary.json').success(function(data) {
   						self.vocabularyFinal = data;
					});

					// Initializing values
					self.onplaying = false;
					self.onpause = true;
					var paused = false;//warning, this is a one shot variable, we need it only once loading the search page
					self.showtagtxt = false;
					self.mtagging = false;

					var myVid = angular.element(window.document.querySelector('#videoarea'));

					self.currentTime = myVid[0].currentTime;//initialize current time
					self.startTagTime = self.currentTime;
					self.currentvidDur = 0;

					// On video playing toggle values
					myVid[0].onplaying = function() {
			    		self.onplaying = true;
			    		self.onpause = false;
			    		self.currentTime = myVid[0].currentTime;//always update current time
			    		if (!paused){
			    			myVid[0].pause();
			    			paused = true;
			    		}
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
					self.pauseVid = function(){     
			    	if ((!myVid[0].paused || !self.onpause) && !self.mtagging) {
			    			self.onpause = true;
			        		self.onplaying = false;
			        		myVid[0].pause();
			    		}
			    	/*else if ((!myVid[0].paused || !self.onpause) && self.mtagging) {
			    			manual tag general mode
			        		self.onpause = true;
			        		self.onplaying = false;
			        		self.mtagging = false;
			        		self.showtagtxt = false;
			    			myVid[0].pause();
			        		sharedProperties.setEndTime(myVid[0].currentTime);
	        				myModalGeoFactory.open('lg', 'myModalGeoCode.html');
			    		}*/
			    	else if (myVid[0].paused && self.onpause) {
			        		self.onpause = false;
			        		self.onplaying = true;
			        		self.showtagtxt = false;
			        		myVid[0].play();
			    		}
					}

					self.manualtag = function(group,labelterm){
						if (self.onpause && !self.onplaying) {
							/*manual tag general mode
							self.mtagging = true;
							self.showtagtxt = true;
							self.startTagTime = myVid[0].currentTime; //set initial tag frame current time
							sharedProperties.setStartTime(self.startTagTime);
							playVid(myVid[0]);*/
							self.startTagTime = myVid[0].currentTime; //set initial tag frame current time
							sharedProperties.setStartTime(self.startTagTime);

							for (var i=0; i<self.items.length-1; i++)
							{

							var time1 = self.items[i][5];
							var time2 = self.items[i+1][5];

							var currtime1 = time1.split("-")[0];
							var hours1 = currtime1.split(":")[0];
							var mins1 = currtime1.split(":")[1];
							var secs1 = currtime1.split(":")[2];
							//var cdate = new Date(0, 0, 0, hours, mins, secs);
							var times1 = (secs1 * 1) + (mins1 * 60) + (hours1 * 3600); //convert to seconds

							var currtime2 = time2.split("-")[0];
							var hours2 = currtime2.split(":")[0];
							var mins2 = currtime2.split(":")[1];
							var secs2 = currtime2.split(":")[2];
							//var cdate = new Date(0, 0, 0, hours, mins, secs);
							var times2 = (secs2 * 1) + (mins2 * 60) + (hours2 * 3600); //convert to seconds

							if (self.startTagTime>=times1 && self.startTagTime<=times2){
									sharedProperties.setStartTime(times1);
									sharedProperties.setEndTime(times2);
									sharedProperties.setGroup(group);
									sharedProperties.setLabelTerm(labelterm);
									myModalGeoFactory.open('lg', 'myModalGeoCode.html');
								}
							}
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
				    					}

				    					setTimeout(function() { 

										//timeline definition
										self.mainchar = '30-60';
										self.outside = '180-250';
										self.crowd = '270-300';

										self.vduration = self.currentvidDur;

										var minutes = 0, hours = 0;
										var seconds = self.vduration;
									    if (seconds / 60 > 0) {
									        minutes = parseInt(seconds / 60, 10);
									        seconds = seconds % 60;
									    }
									    if (minutes / 60 > 0) {
									        hours = parseInt(minutes / 60, 10);
									        minutes = minutes % 60;
									    }

										/*configuration*/
										var videoTimeline = {
											"type": "Timeline",
											"cssStyle": "height: 100%; width: 100%;",
											//"displayed": false,
											"options" : {
												timeline: {showRowLabels: true, colorByRowLabel: true},
												avoidOverlappingGridLines: false,
												hAxis: {
    												minValue: new Date(0,0,0,0,0,0),
   	 												maxValue: new Date(0,0,0,hours,minutes,seconds),
   	 												format: 'HH:mm:ss'
  												}
		        							}
										};

										// add data to the timeline

										videoTimeline.data = {
		    								"cols": [
		    								{id: "category", label: "Category", type: "string"},
		    								{id: "tag", label: "Tag", type: "string"},
		    								{id: "start", label: "Start", type: "date"},
		    								{id: "end", label: "End", type: "date"}
		    							], "rows": []};

		    							videoTimeline.data.rows.push({c: [
								    	   {v: "Location"},
								    	   {v: "Porta S."},
								   	       {v: new Date(0,0,0,0,0,self.outside.split('-')[0])},
								   		   {v: new Date(0,0,0,0,0,self.outside.split('-')[1])}
										]});

										videoTimeline.data.rows.push({c: [
								       		{v: "Location"},
								       		{v: "Porta P."},
								       		{v: new Date(0,0,0,0,0,self.outside.split('-')[0])},
								       		{v: new Date(0,0,0,0,0,self.outside.split('-')[1])}
										]});

		    			 				videoTimeline.data.rows.push({c: [
								    	   {v: "Location"},
								    	   {v: "Via Mazzini"},
								    	   {v: new Date(0,0,0,0,0,self.mainchar.split('-')[0])},
								     	   {v: new Date(0,0,0,0,0,self.mainchar.split('-')[1])}
										]});

										videoTimeline.data.rows.push({c: [
								    	   {v: "Location"},
								    	   {v: "Via Indipendenza"},
								    	   {v: new Date(0,0,0,0,0,self.mainchar.split('-')[0])},
								     	   {v: new Date(0,0,0,0,0,self.mainchar.split('-')[1])}
										]});

										videoTimeline.data.rows.push({c: [
								    	   {v: "Location"},
								    	   {v: "Via Oberdan"},
								    	   {v: new Date(0,0,0,0,0,self.mainchar.split('-')[0])},
								     	   {v: new Date(0,0,0,0,0,self.mainchar.split('-')[1])}
										]});

										videoTimeline.data.rows.push({c: [
								    	   {v: "People"},
								     	  {v: "Crowd"},
								     	  {v: new Date(0,0,0,0,0,self.crowd.split('-')[0])},
								     	  {v: new Date(0,0,0,0,0,self.crowd.split('-')[1])}
										]});

										self.videoTimeline = videoTimeline;

										}, 2000);

									}
								});
						};

					self.loadMetadataContent = function(vid) {
						self.loading = true;
						// console.log('loading metadata content');
						DataService.getVideoMetadata(vid).then(
							function(response) {
								self.video = response.data[0];
								self.currentvidDur = self.video.relationships.item[0].attributes.duration;
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

					self.jumpToShot = function(selectedShot) {
						var row = selectedShot.row;
						if (row !== 0) {
							// ignore 'Duration' row
							var time1 = self.videoTimeline.data.rows[row].c[2].v;
							var time2 = self.videoTimeline.data.rows[row].c[3].v;

							var t1 = time1.getHours()+':'+time1.getMinutes()+':'+time1.getSeconds();
							var t2 = time2.getHours()+':'+time2.getMinutes()+':'+time2.getSeconds();
							var time1c = convertTime(t1);
							var time2c = convertTime(t2);

							// play video from selected shot
							var myVid = angular.element($document[0].querySelector('#videoarea'));
							myVid[0].currentTime = time1c;
							myVid[0].play();
						}
					};

					self.getTagMenu = function(event) {
						  var props = timeline.getEventProperties(event)
  						  alert(props);
					};

					$rootScope.$on('updateTimeline', function(event, locname, startT, endT, group, labelTerm) {
	    				self.videoTimeline.data.rows.push({c: [
							  {v: group},
							  {v: labelTerm+": "+locname},
							  {v: new Date(0,0,0,0,0,startT)},
							  {v: new Date(0,0,0,0,0,endT)}
						]});
	  				});

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
							'number': shot.attributes.shot_num+1,
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

			// Please note that $modalInstance represents a modal window (instance) dependency.
			// It is not the same as the $uibModal service used above.
			function geoTagController($scope, $uibModalInstance, myGeoConfirmFactory, GeoCoder) {
		  	$scope.geocodingResult = "";

		  	$scope.ok = function() {
		    	GeoCoder.geocode({
						address: $scope.tagInput
					})
					.then(function(result) {
						var locationlat = result[0].geometry.location.lat();
						var locationlng = result[0].geometry.location.lng();
						var locname = result[0].formatted_address;//result[0].address_components[0].long_name;
						var restring = '(lat, lng) ' + locationlat + ', ' + locationlng + ' (address: \'' + locname + '\')';
						myGeoConfirmFactory.open('lg', 'result.html', {result: restring, resarr: result});
				});
		    	//$uibModalInstance.close($scope.searchTerm);
		  	};

		  	$scope.cancel = function() {
		    	$uibModalInstance.dismiss('cancel');
		  	};
			}

			function geoResultController($scope, $rootScope, $document, $uibModalInstance, params, sharedProperties) {
			$scope.geocodingResult = params.result;
			$scope.geoResArray = params.resarr;

		  	$scope.ok = function() {
		  		var res = $scope.geocodingResult;
		  		var rarr = $scope.geoResArray;

		  		$scope.startT = sharedProperties.getStartTime();
		  		$scope.endT = sharedProperties.getEndTime();
		  		$scope.group = sharedProperties.getGroup();
		  		$scope.labelTerm = sharedProperties.getLabelTerm();

				$rootScope.$emit('updateTimeline', rarr[0].address_components[0].long_name, $scope.startT, $scope.endT, $scope.group, $scope.labelTerm);

		    	$uibModalInstance.close($scope.tagInput);
		  	};

		  	$scope.cancel = function() {
		    	$uibModalInstance.dismiss('cancel');
		  	};

			}

		})();



