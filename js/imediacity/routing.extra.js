(function() {
'use strict';

loggedLandingPage = "logged.search";

angular.module('web').constant('customRoutes',
{
    'logged.search': {
        url: "/search",
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'search.html',
            }
        }
    },
    'logged.upload': {
        url: "/upload",
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'upload.html',
            }
        }
    }
});

})();
