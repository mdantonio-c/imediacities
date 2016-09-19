(function() {
  'use strict';

angular.module('web').service('DataService', DataService);

function DataService($log, api, $q) {

	var self = this;

    self.getVideos = function() {
        return api.apiCall('video', 'GET');
    }
    self.getVideoInfo = function(video) {
        return api.apiCall('video/'+video+'annotations', 'GET');
    }
}

})();