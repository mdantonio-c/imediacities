(function() {
	'use strict';

	angular.module('web').service('VocabularyService', VocabularyService);


	function VocabularyService($http, $q) {
		var vocabulary = {};

		vocabulary.terms = [];

		vocabulary.loadTerms = function() {
			var d = $q.defer();
			if (vocabulary.terms.length > 0) {
				d.resolve(vocabulary.terms);
			}
			else {
				// console.log('load vocabulary from server');
				$http.get('static/assets/vocabulary/vocabulary.json')
				.success(function(data) {
					vocabulary.terms = data.terms;
					d.resolve(data.terms);
				})
				.error(function(reason) {
					d.reject(reason);
				});
			}
			return d.promise;
		};

		return vocabulary;
	};

	VocabularyService.$inject = ["$http", "$q"];
})();