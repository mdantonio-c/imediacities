(function() {
	'use strict';

	angular.module('web').service('CodelistService', function($http, $q, DataService) {
		var codelist = {};

		// this is the structure of the codelist object
		// codelist["en"]["countries"] = []

		codelist.loadTerms = function(lang,name) {
			var d = $q.defer();
			if (!name) {
				d.reject();
			}else{
				if (!lang) {
					lang='en';
				}
				if (codelist[lang] && codelist[lang][name] && codelist[lang][name].length > 0) {
					d.resolve(codelist[lang][name]);
				}
				else {
					codelist[lang]={};
					codelist[lang][name]={};
					console.log("Loading codelist '" + name + "," + lang + "' from server");
					DataService.getFcodelist(name,lang).then(
					function(response) {
						codelist[lang][name] = response.data;
						d.resolve(codelist[lang][name]);
					},
					function(reason) {
						console.log('Error: ' + reason.errors[0]);
						if(name == "countries"){
							d.resolve(countriesMinimalList);
						}
						d.reject(reason);
					});
				}
			}
			return d.promise;
		};
		return codelist;
	});


// if the backend api does not work
		 var countriesMinimalList = [{
			"code": "IT",
			"name": "Italy"
		}, {
			"code": "AT",
			"name": "Austria"
		}, {
			"code": "BE",
			"name": "Belgium"
		}, {
			"code": "DE",
			"name": "Germany"
		}, {
			"code": "ES",
			"name": "Spain"
		}, {
			"code": "FI",
			"name": "Finland"
		}, {
			"code": "FR",
			"name": "France"
		}, {
			"code": "GB",
			"name": "United Kingdom"
		}, {
			"code": "GR",
			"name": "Greece"
		}];

})();
