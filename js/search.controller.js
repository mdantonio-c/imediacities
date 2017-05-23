(function() {
  'use strict';

var app = angular.module('web').controller('SearchController', SearchController);

// create a simple search filter
app.filter('searchFor', function() {
	return function(arr, searchString) {
		if(!searchString){
			return arr;
		}

		var result = [];

		searchString = searchString.toLowerCase();

		angular.forEach(arr, function(item){
			if(item.title.toLowerCase().indexOf(searchString) !== -1){
				result.push(item);
			}
		});

		return result;
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
		var currtime = (duration/nshots)*progr;
		myVid[0].currentTime = currtime;
		myVid[0].play();
      });
    }
  }
});

function getElement(event) {
	return angular.element(event.srcElement || event.target);
}

// The controller
function SearchController($scope, $log, $document, $http, $auth, DataService, noty, NgMap)
{
	var self = this;

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
			    var frameshot = [2];
			    frameshot[0] = start_frame;
				frameshot[1] = self.video.relationships.item[0].attributes.duration;
				frameshot[2] = self.shots.length;
				frameshot[3] = i;
			    frameshot[4] = thumblink;
				$scope.items.push(frameshot); 
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


    	/*self.mainchar = self.video.frames[0].mainchar;
    	self.outside = self.video.frames[1].outside;

    	// add data to the timeline
		$scope.videoTimeline.data = {
    		"cols": [
    			{id: "category", label: "Category", type: "string"},
    			{id: "tag", label: "Tag", type: "string"},
    			{id: "start", label: "Start", type: "date"},
    			{id: "end", label: "End", type: "date"}
    		], "rows": [
    			{c: [
		            {v: "Video"},
		            {v: "Duration"},
		            {v: new Date(0,0,0,0,0,0)},
		            {v: new Date(0,0,0,0,0,self.video.duration)}
		        ]},
		        {c: [
		            {v: "Video"},
		            {v: "Main Char"},
		            {v: new Date(0,0,0,0,0,self.mainchar.split('-')[0])},
		            {v: new Date(0,0,0,0,0,self.mainchar.split('-')[1])}
		        ]},
		        {c: [
		            {v: "Video"},
		            {v: "Outside"},
		            {v: new Date(0,0,0,0,0,self.outside.split('-')[0])},
		            {v: new Date(0,0,0,0,0,self.outside.split('-')[1])}
		        ]}
    		]
    	}*/
    	//$scope.loadVideo(video.id);
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

})();
