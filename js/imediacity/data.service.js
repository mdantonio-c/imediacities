(function() {
  'use strict';

angular.module('web').service('DataService', DataService);

function DataService($log, api, $q, jsonapi_parser) {

	var self = this;

    self.getVideos = function() {
        return api.apiCall('video', 'GET');
    }
    self.getVideoInfo = function(video) {
        return api.apiCall('video/'+video+'annotations', 'GET');
    }


    self.getUserSchema = function(study) {
        return api.apiCall('admin/users', 'POST');
    }
    self.getUsers = function() {
        var endpoint = 'admin/users'
        return jsonapi_parser.parseResponse(api.apiCall(endpoint, 'GET'));
    }
    self.saveUser = function(data) {
        return api.apiCall('admin/users', 'POST', data);
    }
    self.deleteUser = function(user) {
        return api.apiCall('admin/users/'+user, 'DELETE');
    }
    self.updateUser = function(user, data) {
        return api.apiCall('admin/users/'+user, 'PUT', data);
    }


    self.getGroupSchema = function(study) {
        return api.apiCall('admin/groups', 'POST');
    }
    self.getGroups = function() {
        var endpoint = 'admin/groups'
        return jsonapi_parser.parseResponse(api.apiCall(endpoint, 'GET'));
    }
    self.saveGroup = function(data) {
        return api.apiCall('admin/groups', 'POST', data);
    }
    self.deleteGroup = function(group) {
        return api.apiCall('admin/groups/'+group, 'DELETE');
    }
    self.updateGroup = function(group, data) {
        return api.apiCall('admin/groups/'+group, 'PUT', data);
    }

    self.getUserGroups = function(query) {
        var endpoint = 'group/'+query
        return api.apiCall(endpoint, 'GET');
    }
    
}

})();