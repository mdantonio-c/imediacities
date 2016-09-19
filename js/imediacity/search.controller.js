(function() {
  'use strict';

angular.module('web').controller('SearchController', SearchController);

function SearchController($scope, $log, DataService, noty)
{
	var self = this;

	self.videos = []

	self.loading = true;
	DataService.getVideos().then(
		function(out_data) {
			self.videos = out_data.data;
			self.loading = false;

            noty.extractErrors(out_data, noty.WARNING);
		}, function(out_data) {
			self.loading = false;
			self.studyCount = 0;

            noty.extractErrors(out_data, noty.ERROR);
		});
}

})();