(function() {
  'use strict';

var app = angular.module('web').controller('StageController', StageController);

// The controller
function StageController($scope, $log, DataService, noty)
{
	var self = this;

	self.videos = []

	self.loading = true;
	DataService.getStageFiles().then(
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