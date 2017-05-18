(function() {
  'use strict';

angular.module('web').service('DataService', DataService);

function DataService($log, api, $q, jsonapi_parser) {

	var self = this;

    self.getParametersSchema = function(endpoint) {
        return api.apiCall("schemas/"+endpoint, 'GET');
    }

    self.searchVideos = function(data) {
        return api.apiCall('search', 'POST', data);
    }

    self.getStageFiles = function(group) {

        if (typeof group !== 'undefined') { 
            return jsonapi_parser.parseResponse(api.apiCall('stage/'+group, 'GET'));
        }

        return jsonapi_parser.parseResponse(api.apiCall('stage', 'GET'));
    }
    self.importStageFiles = function(file) {
        var data = {"filename": file}
        return api.apiCall('stage', 'POST', data);
    }
    self.deleteStageFile = function(file) {
        var data = {"filename": file}
        return api.apiCall('stage', 'DELETE', data);
    }

    // self.getVideos = function() {
    //     return jsonapi_parser.parseResponse(api.apiCall('video', 'GET'));
    // }
    // self.getVideoInfo = function(video) {
    //     return api.apiCall('video/'+video+'annotations', 'GET');
    // }


    self.getUserSchema = function(study) {
        // return api.apiCall('admin/users', 'POST');
        return self.getParametersSchema('admin/users');
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
        var data = {'get_schema': true}
        return api.apiCall('admin/groups', 'POST', data);
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
    self.getUserRoles = function(query) {
        var endpoint = 'role/'+query
        return api.apiCall(endpoint, 'GET');
    }

}

})();
