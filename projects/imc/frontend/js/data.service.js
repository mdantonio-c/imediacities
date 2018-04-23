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

    //
    // IMAGES
    //
    self.getImageMetadata = function(imageId) {
        return api.apiCall('images/'+imageId, 'GET');
    };
    self.getImageAnnotations = function(imageId) {
         return api.apiCall('images/'+imageId+'/annotations', 'GET');
    };

    //
    // VIDEOS
    //

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
                };
            } else {
                body.value = tags[0].label;
            }
            data.body = body;
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
                    };
                } else {
                    body.value = tag.label;
                }
                bodies.push(body);
            });
            data.body = bodies;
        }
        data.motivation = "tagging";
        return api.apiCall('annotations', 'POST', data);
    };

    self.saveNote = function(target, note) {
        var data = {};
        data.target = target;
        var body = {};
        body.type = "TextualBody";
        body.value = note.text;
        if(note.languageCode && note.languageCode !== ""){
            body.language = note.languageCode;
        }else{
            body.language = null;
        }
        data.body = body;
        if(note.privacy == "public"){
            data.private = false;
        } else{
            data.private = true;            
        }
        // TODO manca embargo
        data.motivation = "describing";
        if(note && note.id){
            // update existing note
            return api.apiCall('annotations/'+note.id, 'PUT', data);
        }else{
            // create a new note
            return api.apiCall('annotations', 'POST', data);            
        }
    };

    self.saveGeoAnnotation = function(target, source, spatial) {
        var data = {
            target: target,
            body: {
                type: "ResourceBody",
                purpose: "tagging",
                source: source,
                spatial: spatial
            }
        };
        data.motivation = "tagging";
        return api.apiCall('annotations', 'POST', data);  
    };

    self.getManualSegments = function(videoId) {
/*        return jsonapi_parser.parseResponse(
            api.apiCall(
                'videos/'+videoId+'/annotations?type=TVS&onlyManual', 'GET'
                )
            );
*/
        return api.apiCall(
            'videos/'+videoId+'/annotations?type=TVS&onlyManual', 'GET'
        );
    }
    self.saveManualSegment = function(target, startFrame, endFrame) {
        var data = {
            target: target,
            body: {
                type: "TVSBody",
                segments: ["t="+startFrame+","+endFrame]
            },
            motivation: "segmentation"
        }

        return api.apiCall('annotations', 'POST', data);  
    }

    self.deleteManualSegment = function(uuid) {
        return api.apiCall('annotations/'+uuid, 'DELETE');
    }

    self.deleteAnnotation = function (annoId, bodyRef) {
        if (bodyRef !== undefined) {
            return api.apiCall('annotations/'+annoId+'?body_ref='+encodeURIComponent(bodyRef), 'DELETE');
        } else {
            return api.apiCall('annotations/'+annoId, 'DELETE');
        }
    };
    self.deleteNote = function (noteId) {
        return api.apiCall('annotations/'+noteId, 'DELETE');
    };

    self.getGeoDistanceAnnotations = function (distance, pin, cFilter) {
        var filter = {
            filter: {
                type: "TAG",
                geo_distance: {
                    distance: distance,
                    location: {
                        lat: pin[0],
                        long: pin[1]
                    }
                }
            }
        };
        if (cFilter !== undefined) {
            filter.filter.creation = cFilter;
        }
        return api.apiCall('annotations/search', 'POST', filter, undefined, true);
    };

    /* Retrieve a list of relevant creations for given creation uuids and related place ids. */
    self.getRelavantCreations = function(relevantCreations) {
        if (relevantCreations === undefined || relevantCreations.size === 0) { 
            var d = $q.defer();
            d.resolve({'data': {'Response': {'data': []}}});
            return d.promise; 
        }
        var data = {
            'relevant-list': []
        };
        for (var uuid of relevantCreations.keys()) {
            var item = {
                'creation-id': uuid,
                'place-ids': Array.from(relevantCreations.get(uuid))
            };
            data['relevant-list'].push(item);
        }
        return api.apiCall('search_place', 'POST', data, undefined, true);
    };

    self.saveUser = function(data) {
        return api.apiCall('custom_admin/users', 'POST', data);
    };

    self.deleteUser = function(user) {
        return api.apiCall('custom_admin/users/'+user, 'DELETE');
    };

    self.updateUser = function(user, data) {
        return api.apiCall('custom_admin/users/'+user, 'PUT', data);
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

    self.getFcodelist = function(name,lang) {
        var endpoint = 'fcodelist/'+name+'?lang='+lang;
        return api.apiCall(endpoint, 'GET');
    };

}

})();
