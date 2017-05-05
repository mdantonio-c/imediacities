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
    restrict: 'A',
    link: function($scope, $elm) {
      $elm.on('click', function() {
        $(".scrollmenu").animate({scrollLeft: $elm.offset().left}, "slow");
      });
    }
  }
});

function getElement(event) {
	return angular.element(event.srcElement || event.target);
}

// The controller
function SearchController($scope, $log, $document, DataService, noty, NgMap)
{
	var self = this;

	/*filling the scrolling bar with the image shots*/
	$scope.items = [];
  	for (var i=1; i<9; i++) { $scope.items.push(i); }

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
	DataService.searchVideos().then(
		function(out_data) {
			self.videos = out_data.data;
			self.loading = false;

            noty.extractErrors(out_data, noty.WARNING);
		}, function(out_data) {
			self.loading = false;
			self.studyCount = 0;

            noty.extractErrors(out_data, noty.ERROR);
		});
	//self.videos = loadSampleVideos();

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

	$scope.loadVideoContent = function(video) {
		self.video = video;
		self.selectedVideo = true;
		self.selectedVideoId = video.id;

		NgMap.getMap({id:'videomap'}).then(function(map) {
      		google.maps.event.trigger(map,'resize');
    	});

    	self.mainchar = self.video.frames[0].mainchar;
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
    	}
	};

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

/*function loadSampleVideos() {
	var videos = [
		{
                        "id": "1",
                        "title": "Bologna Ieri e Oggi",
                        "duration": "433",
                        "movieurl": "http://130.186.13.19/static/assets/videos/BolognaIeriEOggi.mp4",
                        "moviesposter": "http://www.cinetecadibologna.it/imageserver/lightboxenlarge/files/festival/CinemaRitrovato/2012/1912/Bologna.jpg",
                        "year": "1921",
                        "description": "Dopo aver fatto il giro del mondo torniamo nel nostro paese, cento anni fa. ‘Un paese antico, moderno, anzi pittoresco’: nel 1911 viene fondata a Milano la società cinematografica Panorami Italici, costituita, come da statuto, per realizzare e promuovere “cinematografie delle bellezze italiane all’estero”. Nel 1912 l’Ambrosio inaugura la serie Bellezze italiche che si impegna a filmare gli scorci più suggestivi del paesaggio italiano. Le riproduzioni filmate delle meraviglie naturali, delle rovine storiche, delle città monumentali italiane sono particolarmente apprezzate dagli spettatori stranieri che possono godere di un Grand Tour virtuale a basso costo. ",
                        "locname": "Bologna",
                        "location": [
                                {"lat": "44.5019603", "lng": "11.2855505"}
                        ],
                        "frames": [
                                {"mainchar": "100-200"},
                                {"outside": "300-400"}
                        ]
                },
                {
                        "id": "2",
                        "title": "L'Italia negli anni 60",
                        "duration": "414",
                        "movieurl": "http://130.186.13.19/static/assets/videos/ItaliaAnni60.mp4",
                        "moviesposter": "http://www.panoramio.com/photos/original/7143296.jpg",
                        "year": "1960",
                        "description": "Documentario sull'Italia negli anni del boom economico, con immagini di repertorio dell'epoca...",
                        "locname": "Italy",
                        "location":[
                                {"lat": "44.7", "lng": "12.9"}
                        ],
                        "frames": [
                                {"mainchar": "50-80"},
                                {"outside": "200-300"}
                        ]
                }
		/*{
			"id": "1",
			"title": "Happy Feet",
			"duration": "82",
			"movieurl": "http://html5videoformatconverter.com/data/images/happyfit2.mp4",
			"moviesposter": "http://html5videoformatconverter.com/data/images/screen.jpg",
			"year": "2006",
			"description": "Into the world of the Emperor Penguins, who find their soul mates through song, a penguin is born who cannot sing. But he can tap dance something fierce!",
			"locname": "south pole",
			"location": [
				{"lat": "-67.222", "lng": "78.98"}
			],
			"frames": [
				{"mainchar": "10-20"},
				{"outside": "30-40"}
			]
		},
		{
			"id": "2",
			"title": "Sintel",
			"duration": "52",
			"movieurl": "http://grochtdreis.de/fuer-jsfiddle/video/sintel_trailer-480.mp4",
			"moviesposter": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Sintel_movie_4K.webm/500px-seek%3D120-Sintel_movie_4K.webm.jpg",
			"year": "2010",
			"description": "The film follows a girl named Sintel who is searching for a baby dragon she calls Scales. A flashback reveals that Sintel found Scales with its wing injured and helped care for it, forming a close bond with it. By the time its wing recovered and it was able to fly, Scales was caught by an adult dragon.",
			"locname": "greenland",
			"location":[
				{"lat": "55.3", "lng": "-45.45"}
			],
			"frames": [
				{"mainchar": "5-20"},
				{"outside": "30-40"}
			]
		},
		{
			"id": "3",
			"title": "Big Buck Bunny",
			"duration": "60",
			"movieurl": "http://www.ioncannon.net/examples/vp8-webm/big_buck_bunny_480p.webm",
			"moviesposter": "http://a2.mzstatic.com/us/r30/Purple/v4/ac/fb/fb/acfbfb6f-d262-d888-ecfe-d6f4ceb7169c/screen480x480.jpeg",
			"year": "2008",
			"description": "Big Buck Bunny (code-named Peach) is a short computer-animated comedy film by the Blender Institute, part of the Blender Foundation. Like the foundation's previous film Elephants Dream, the film was made using Blender, a free software application for animation made by the same foundation. It was released as an open-source film under Creative Commons License Attribution 3.0.",
			"locname": "mozambique",
			"location":[
				{"lat": "-14.234", "lng": "41.504"}
			],
			"frames": [
				{"mainchar": "30-40"},
				{"outside": "5-10"}
			]
		}];
	return videos;
}*/

})();
