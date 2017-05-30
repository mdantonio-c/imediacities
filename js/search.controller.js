				(function() {
				  'use strict';

				var app = angular.module('web').controller('SearchController', SearchController);

				/*modal view storyboard factory definition*/
				app.factory('modalFactory', function($uibModal) {
				    return {
				      open: function(size, template, params) {
				        return $uibModal.open({
				          animation: false,
				          templateUrl: template || 'myModalContent.html',
				          controller: 'ModalResultInstanceCtrl',
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
					return function(arr, searchString) {
						if(searchString === '*'){
							return arr;
						}
						else if (searchString){

						var result = [];

						searchString = searchString.toLowerCase();

						angular.forEach(arr, function(item){
							if(item.attributes.identifying_title.toLowerCase().indexOf(searchString) !== -1){
								result.push(item);
							}
						});

						return result;
						}
					}
				}).filter('trustUrl', function($sce) {
					return function(url) {
						return $sce.trustAsResourceUrl(url);
					};
				});

				app.directive('scrollOnClick', function() {
				  return {
				    //restrict: 'A',
				    link: function($scope, $elm) {
				      $elm.on('click', function() {
				      	//alert($elm[0].parentNode.className);
				        $(".scrollmenu").animate({scrollLeft: $elm.offset().left}, "slow");
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
						var cdate = new Date(0,0,0,hours,mins,secs);
						var times =  (secs*1)+(mins*60)+(hours*3600);//convert to seconds

						myVid[0].pause();
						myVid[0].currentTime = times;
						myVid[0].play();

				      });
				    }
				  }
			});

			function getElement(event) {
					return angular.element(event.srcElement || event.target);
			}

			// The controller
			function SearchController($scope, $log, $document, $http, $auth, DataService, noty, NgMap, $uibModal)
			{
					var self = this;

					self.showmesb = false;

					/*$scope.overMouseEvent = function(event) {

					var elm = getElement(event);

				        switch (event.type) {
				          case "mouseover":
							$(".scrollmenu").animate({scrollLeft: elm.offset().left}, "slow");
					  default:
							break;
				        	}
				    	}*/
					/*---*/

					self.videos = []

					self.loading = true;
					var request_data = {
						"type": "video",
						"term": "bologna"
					};
					
					DataService.searchVideos(request_data).then(
						function(out_data) {
							self.videos = out_data.data;
							self.loading = false;

				            noty.extractErrors(out_data, noty.WARNING);
						}, function(out_data) {
							self.loading = false;
							self.studyCount = 0;

				            noty.extractErrors(out_data, noty.ERROR);
						});


				/*modal creation*/
				var modalInstance;

				$scope.videoid = self.selectedVideoId;

				  $scope.open = function(size, template) {
				      modalInstance = $uibModal.open({
				          animation: $scope.animationsEnabled,
				          templateUrl: template || 'myModalContent.html',
				          controller: 'ModalInstanceCtrl',
				          size: size,
						  resolve: {
			                   params: function () {
			                   	  var params = {};
			        			  angular.extend(params, {'videoid' : self.selectedVideoId, 'summary' : self.video.links.summary});
			                      return params;
			                   }
			               }
				        });

				      /*modalInstance.result.then(function(selectedItem) {
				        $scope.selected = selectedItem;
				      }, function() {
				        $log.info('Modal dismissed at: ' + new Date());
				      });*/
				    };

				    /*---*/


				    $scope.toggleAnimation = function() {
				      $scope.animationsEnabled = !$scope.animationsEnabled;
				    };

					self.selectedVideo = false;
					self.setectedVideoId = -1;
					self.video = {};
					self.videoMap = {};
					self.googleMapsUrl="https://maps.googleapis.com/maps/api/js?key=AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI";

					// timeline
					self.mainchar = '';
					self.outside = '';

					var videoTimeline = {
						"type": "Timeline",
						"cssStyle": "height: 100%; padding-left: 10px;",
						//"displayed": false,
						"options" : {
							timeline: { showRowLabels: false },
							avoidOverlappingGridLines: false
				        }
					};

					$scope.videoTimeline = videoTimeline;

					self.videoUrl = '';
					$scope.getVideoService = function (videoId) {
						var apiUrl =  'http://localhost:8081/api/videos/'+videoId+'/content?type=video';
						return $http.get(apiUrl, {
				            	responseType: 'blob',
				            	headers: { 
				            		'Content-Type': 'application/json',
				                    'Authorization': 'Bearer ' + DataService.getToken()
				                }
				        	});
				    };

					$scope.loadVideo = function(videoId) {
						console.log('loading video ' + videoId)
						//DataService.getVideoContent(videoId).then(function(response){
						$scope.getVideoService(videoId).then(function(response){
							var videoBlob = new Blob([response.data], { type: response.headers('Content-Type') });
							console.log(videoBlob.size);
							console.log(videoBlob.type);
							self.videoUrl = (window.URL || window.webkitURL).createObjectURL(videoBlob);
						});
					};


					$scope.loadVideoContent = function(video) {
						self.video = video;
						self.selectedVideo = true;
						self.selectedVideoId = video.id;

						$scope.geocoder = new google.maps.Geocoder();

					/*start geocoding and get video coordinates*/
			  		$scope.geocoder.geocode({ 'address': 'Bologna, It' }, function (results, status) {
					if (status === google.maps.GeocoderStatus.OK) {
		   				 if (results[0]) {
		        			$scope.address = results[0].address_components;

		        			var Lat = results[0].geometry.location.lat();
			      			var Lng = results[0].geometry.location.lng();

			      			$scope.videolat = Lat;
							$scope.videolng  = Lng;
							$scope.locname = $scope.address[0].long_name;


					NgMap.getMap({id:'videomap'}).then(function(map) {
				      		google.maps.event.trigger(map,'resize');
				    });


					/*filling the scrolling bar with the image shots*/
					$scope.items = [];
				  	//for (var i=1; i<9; i++) { $scope.items.push(i); }


				  		DataService.getVideoShots(self.selectedVideoId).then(
						function(out_data) {
							self.shots = out_data.data;
							for (var i=0; i<self.shots.length; i++) { 
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

								$scope.items.push(frameshot); 

								$scope.showmesb = true; //enable storyboard button

							}
						});

				  	/*----*/


				  	/*get annotations*/

				  	  	/*DataService.getVideoAnnotations(self.selectedVideoId).then(
						function(out_data) {
							self.annotations = out_data.data;
							for (var i=0; i<self.annotations.length; i++) {}
						});*/

				  	 /*--*/


 				} else {
		        	console.log('Location not found');
		        	$scope.firstExecution = false;
		    	}
				} else {
		       		console.log('Geocoder failed due to: ' + status);
		       	$scope.firstExecution = false;
				}
				});


					};

					  /*$scope.videoTimeline.data.rows.push({c: [
						            {v: "Video"},
						            {v: "Outside 3"},
						            {v: new Date(0,0,0,0,0,self.outside.split('-')[0])},
						            {v: new Date(0,0,0,0,0,self.outside.split('-')[1])}
						        ]});*/


					$scope.jumpToShot = function(selectedShot) {
						var row = selectedShot.row;
						if (row != 0) {	// ignore 'Duration' row
							var time1 = $scope.videoTimeline.data.rows[row].c[2].v.getSeconds();
							var time2 = $scope.videoTimeline.data.rows[row].c[3].v.getSeconds();

							// play video from selected shot
							var myVid = angular.element($document[0].querySelector('#videoarea'));
							myVid[0].currentTime = time1;
							myVid[0].play();
						}
					};


			}



				// storyboard modal view
				// Please note that $modalInstance represents a modal window (instance) dependency.
				// It is not the same as the $uibModal service used above.

				angular.module('web').controller('ModalInstanceCtrl', function($scope, $uibModalInstance, modalFactory, DataService, params) {

				  //$scope.searchTerm = term;

				    /*storyboard definition*/
								 /* $scope.shots = [
				                    { 'thumb':'shot1.png',
				                    	'number': '001',
				                    	'duration': '50',...
								         ]; */

					/*filling the storyboard with the image shots*/

					    $scope.videoid = params.videoid;
					    $scope.summary = params.summary;
					    $scope.shots = [];

				  		DataService.getVideoShots($scope.videoid).then(
						function(out_data) {
							self.shots = out_data.data;
							for (var i=0; i<self.shots.length; i++) { 
							    var thumblink = self.shots[i].links.thumbnail;
							    var start_frame = self.shots[i].attributes.start_frame_idx;
							    var shot_duration = parseInt(self.shots[i].attributes.duration);
							    var timestamp = self.shots[i].attributes.timestamp;
							    var frameshot = [];
								$scope.shots.push({ 'thumb': thumblink, 'number': start_frame, 'timestamp': timestamp, 'duration': shot_duration, 'camera': 'unknown' }); 
							}
						});

				  	/*----*/


				$scope.addRow = function(){		
					$scope.shots.push({ 'name':$scope.name, 'employees': $scope.employees, 'headoffice':$scope.headoffice });
					$scope.name='';
					$scope.employees='';
					$scope.headoffice='';
				};
				$scope.removeRow = function(name){				
						var index = -1;		
						var comArr = eval( $scope.shots );
						for( var i = 0; i < comArr.length; i++ ) {
							if( comArr[i].name === name ) {
								index = i;
								break;
							}
						}
						if( index === -1 ) {
							alert( "Something gone wrong" );
						}
						$scope.shots.splice( index, 1 );		
					};
				/*---*/

				  $scope.showsummary = function() {
				    modalFactory.open('lg', 'result.html', {animation: false, summary: $scope.summary});
				    //$uibModalInstance.close($scope.summary);
				  };

				  $scope.cancel = function() {
				    $uibModalInstance.dismiss('cancel');
				  };

				});

				angular.module('web').controller('ModalResultInstanceCtrl', function($scope, $uibModalInstance, params) {

				  $scope.summary = params.summary;

				  $scope.cancel = function() {
				    $uibModalInstance.dismiss('cancel');
				  };

				})

				//modal view storyboard management

				})();
