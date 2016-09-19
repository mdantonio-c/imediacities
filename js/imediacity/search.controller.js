(function() {
  'use strict';

angular.module('web').controller('SearchController', SearchController);

function SearchController($scope, $log)
{
	var self = this;

	self.videos = [
		{"title": "test", "description": "This is a video test"}
	]
}

})();