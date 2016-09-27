(function() {
  'use strict';

/* Define another module?
console.log('PRE');
angular.module('blueprint', ['ui.router']);
console.log('POST');
*/

  angular
    .module('web', [
        'ngSanitize',
        'ui.router',
        'ui.bootstrap',
        'satellizer',
        'cfp.hotkeys',
        'formly',
        'formlyBootstrap'
    ]);

})();
