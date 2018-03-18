(function() {
  'use strict';

angular.module('web').service('DataService', DataService);

function DataService(ApiService2, jsonapi_parser) {

	var self = this;

    self.getParametersSchema = function(endpoint) {
        return ApiService2.get("schemas/"+endpoint).toPromise();
    };

    self.searchCreations = function(data, currentpage, perpage) {
        return ApiService2.post(
            'search?currentpage='+currentpage+'&perpage='+perpage,
            data,
            {"rawResponse": true}
        ).toPromise();
    };

    self.getStageFiles = function(group) {
        return jsonapi_parser.parseResponse(ApiService2.get('stage', group));
    };
    self.importStageFiles = function(file) {
        return ApiService2.post('stage', {"filename": file}).toPromise();
    };
    self.deleteStageFile = function(file) {
        return ApiService2.delete('stage', {"filename": file}).toPromise();
    };

    self.downloadStageFile = function(filename) {
        var config = {'responseType': 'arraybuffer'};
        return ApiService2.get('download/'+filename, "", {}, {"rawResponse": true, "conf": config}).toPromise();
    };

    self.getVideoMetadata = function(videoId) {
        return ApiService2.get('videos', videoId).toPromise();
    };

    self.getVideoAnnotations = function(videoId) {
         return ApiService2.get('videos/'+videoId+'/annotations').toPromise();
    };

    self.getVideoContent = function(videoId) {
        return ApiService2.get('videos/'+videoId+'/content',"", {}, {"rawResponse": true});
    };

    self.getVideoThumbnail = function(videoId) {
        return ApiService2.get('videos/'+videoId+'/thumbnail').toPromise();
    };

    self.getVideoShots = function(videoId) {
        return ApiService2.get('videos/'+videoId+'/shots').toPromise();
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

        return ApiService2.post('annotations', data).toPromise();
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
        return ApiService2.post('annotations', data).toPromise();
    };

    self.deleteAnnotation = function (annoId, bodyRef) {
        if (bodyRef !== undefined) {
            return ApiService2.delete('annotations/'+annoId+'?body_ref='+encodeURIComponent(bodyRef)).toPromise();
        } else {
            return ApiService2.delete('annotations/', annoId).toPromise();
        }
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
        console.log(angular.toJson(filter, true));
        return ApiService2.post('annotations/search', filter, {"rawResponse": true}).toPromise();
    };

    self.getGroupSchema = function(study) {
        var data = {'get_schema': true};
        return ApiService2.post('admin/groups', data).toPromise();
    };

    self.getGroups = function() {
        return jsonapi_parser.parseResponse(ApiService2.get('admin/groups'));
    };

    self.saveGroup = function(data) {
        return ApiService2.post('admin/groups', data).toPromise();
    };

    self.deleteGroup = function(group) {
        return ApiService2.delete('admin/groups', group).toPromise();
    };

    self.updateGroup = function(group, data) {
        return ApiService2.put('admin/groups', group, data).toPromise();
    };

    self.getFcodelist = function(name,lang) {
        var endpoint = 'fcodelist/'+name+'?lang='+lang;
        return ApiService2.get(endpoint).toPromise();
    };

};

DataService.$inject = ["ApiService2", "jsonapi_parser"];

})();
