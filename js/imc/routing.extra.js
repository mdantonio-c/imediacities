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
    },

    'logged.admin': {
        url: "/admin",
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'admin.html'
            }
        }
    },

    'logged.admin.users': {
        url: "/users",
        views: {
            "admin@logged.admin": {
                dir: 'blueprint',
                templateUrl: 'admin.users.html'
            }
        }
    },

    'logged.admin.groups': {
        url: "/groups",
        views: {
            "admin@logged.admin": {
                dir: 'blueprint',
                templateUrl: 'admin.groups.html'
            }
        }
    },

    'logged.admin.queue': {
        url: "/queue",
        views: {
            "admin@logged.admin": {
                dir: 'base',
                templateUrl: 'admin.queue.html'
            }
        }
    }

});

})();
