(function() {
'use strict';

loggedLandingPage = "logged.search";

angular.module('web').constant('customRoutes',
 {
// JUST A TEST
// Note: this will automatically check api online as not subchild of 'logged'
    'logged.search': {
        url: "/search",
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                // OR
                //dir: 'base',
                templateUrl: 'search.html',
            }
        }
    }
///////////////
 });

})();
