(function() {
  'use strict';

angular.module('web').service('DataService', DataService);

function DataService($log, api, $q, jsonapi_parser) {

	var self = this;

    self.getParametersSchema = function(endpoint) {
        return api.apiCall("schemas/"+endpoint, 'GET');
    };

    self.getToken = function() {
        return api.checkToken();
    };

    self.searchCreations = function(data, currentpage, perpage) {
        return api.apiCall('search?currentpage='+currentpage+'&perpage='+perpage, 'POST', data, undefined, true);
    };

    self.getStageFiles = function(group) {

        if (typeof group !== 'undefined') { 
            return jsonapi_parser.parseResponse(api.apiCall('stage/'+group, 'GET'));
        }

        return jsonapi_parser.parseResponse(api.apiCall('stage', 'GET'));
    };
    self.importStageFiles = function(file) {
        var data = {"filename": file};
        return api.apiCall('stage', 'POST', data);
    };
    self.deleteStageFile = function(file) {
        var data = {"filename": file};
        return api.apiCall('stage', 'DELETE', data);
    };

    self.downloadStageFile = function(filename) {
        var config = {'responseType': 'arraybuffer'};
        return api.apiCall('download/'+filename, 'GET', {}, undefined, true, false, false, config);
    };

    // self.getVideos = function() {
    //     return jsonapi_parser.parseResponse(api.apiCall('video', 'GET'));
    // }

    self.getVideoMetadata = function(videoId) {
        return api.apiCall('videos/'+videoId, 'GET');
    };

    self.getVideoAnnotations = function(videoId) {
         return api.apiCall('videos/'+videoId+'/annotations', 'GET');
    };

    self.getVideoContent = function(videoId) {
        return api.apiCall('videos/'+videoId+'/content', 'GET', {}, undefined, true);
    };

    self.getVideoThumbnail = function(videoId) {
        return api.apiCall('videos/'+videoId+'/thumbnail', 'GET');
    };

    self.getVideoShots = function(videoId) {
        return api.apiCall('videos/'+videoId+'/shots', 'GET');
    };

    self.getUserSchema = function(study) {
        // return api.apiCall('admin/users', 'POST');
        return self.getParametersSchema('admin/users');
    };

    self.getUsers = function() {
        var endpoint = 'admin/users';
        return jsonapi_parser.parseResponse(api.apiCall(endpoint, 'GET'));
    };

    self.saveTagAnnotations = function(target, tags) {
        var data = {};
        data.target = target;
        if (tags.length === 1) {
            var body = {};
            body.type = (tags[0].iri !== undefined) ? "ResourceBody" : "TextualBody";
            body.purpose = "tagging";
            if (body.type === "ResourceBody") {
                body.source = {
                    iri: tags[0].iri,
                    name: tags[0].label
                }
            } else {
                value: tags[0].label
            }
            data.body = body
        } else {
            var bodies = [];
            angular.forEach(tags, function(tag){
                var body = {
                    type: (tag.iri !== undefined) ? "ResourceBody" : "TextualBody",
                    purpose: "tagging"
                };
                if (body.type === "ResourceBody") {
                    body.source = {
                        iri: tag.iri,
                        name: tag.label
                    }
                } else {
                    body.value = tag.label;
                }
                bodies.push(body)
            });
            data.body = bodies;
        }

        return api.apiCall('annotations', 'POST', data);
    };

    self.saveGeoAnnotation = function(target, source) {
        var data = {};
        data.target = target;
        data.body = {};
        data.body.type = "ResourceBody";
        data.body.purpose = "tagging";
        data.body.source = source;
        return api.apiCall('annotations', 'POST', data);  
    }

    self.deleteAnnotation = function (annoId) {
        return api.apiCall('annotations/'+annoId, 'DELETE');
    };

    self.saveUser = function(data) {
        return api.apiCall('admin/users', 'POST', data);
    };

    self.deleteUser = function(user) {
        return api.apiCall('admin/users/'+user, 'DELETE');
    };

    self.updateUser = function(user, data) {
        return api.apiCall('admin/users/'+user, 'PUT', data);
    };

    self.getGroupSchema = function(study) {
        var data = {'get_schema': true};
        return api.apiCall('admin/groups', 'POST', data);
    };

    self.getGroups = function() {
        var endpoint = 'admin/groups';
        return jsonapi_parser.parseResponse(api.apiCall(endpoint, 'GET'));
    };

    self.saveGroup = function(data) {
        return api.apiCall('admin/groups', 'POST', data);
    };

    self.deleteGroup = function(group) {
        return api.apiCall('admin/groups/'+group, 'DELETE');
    };

    self.updateGroup = function(group, data) {
        return api.apiCall('admin/groups/'+group, 'PUT', data);
    };

    self.getUserGroups = function(query) {
        var endpoint = 'group/'+query;
        return api.apiCall(endpoint, 'GET');
    };

    self.getUserRoles = function(query) {
        var endpoint = 'role/'+query;
        return api.apiCall(endpoint, 'GET');
    };

}

})();
