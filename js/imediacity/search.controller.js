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
});

// The controller
function SearchController($scope, $log, DataService, noty)
{
	var self = this;

/*	self.videos = []

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
		});*/
	self.videos = loadSampleVideos();
}

function loadSampleVideos() {
	var videos = [
		{
			id: '1',
			title: 'Happy Feet',
			duration: '82',
			movieurl: 'http://html5videoformatconverter.com/data/images/happyfit2.mp4',
			moviesposter: 'http://html5videoformatconverter.com/data/images/screen.jpg',
			year: '2006',
			description: 'Into the world of the Emperor Penguins, who find their soul mates through song, a penguin is born who cannot sing. But he can tap dance something fierce!',
			locname: 'south pole',
			location: [
				{lat: '-67.222', lng: '78.98'}
			],
			frames: [
				{mainchar:'10-20'},
				{outside:'30-40'}
			]
		},
		{
			id:'2',
			title: 'Sintel',
			duration:'52',
			movieurl:'http://grochtdreis.de/fuer-jsfiddle/video/sintel_trailer-480.mp4',
			moviesposter:'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Sintel_movie_4K.webm/500px-seek%3D120-Sintel_movie_4K.webm.jpg',
			year:'2010',
			description: 'The film follows a girl named Sintel who is searching for a baby dragon she calls Scales. A flashback reveals that Sintel found Scales with its wing injured and helped care for it, forming a close bond with it. By the time its wing recovered and it was able to fly, Scales was caught by an adult dragon.',
			locname: 'greenland',
			location:[
				{lat: '55.3', lng: '-45.45'}
			],
			frames:[
				{mainchar: '5-10'},
				{outside: '30-40'}
			]},
		{
			id: '3',
			title: 'Big Buck Bunny',
			duration: '60',
			movieurl: 'http://www.ioncannon.net/examples/vp8-webm/big_buck_bunny_480p.webm',
			moviesposter: 'http://a2.mzstatic.com/us/r30/Purple/v4/ac/fb/fb/acfbfb6f-d262-d888-ecfe-d6f4ceb7169c/screen480x480.jpeg',
			year: '2008',
			description: "Big Buck Bunny (code-named Peach) is a short computer-animated comedy film by the Blender Institute, part of the Blender Foundation. Like the foundation's previous film Elephants Dream, the film was made using Blender, a free software application for animation made by the same foundation. It was released as an open-source film under Creative Commons License Attribution 3.0.",
			locname: 'mozambique',
			location:[
				{lat: '-14.234', lng: '41.504'}
			],
			frames:[
				{mainchar:'30-40'},
				{outside:'5-10'}
			]
		}];
	return videos;
}

})();