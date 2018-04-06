(function() {
'use strict';

angular.module('web').constant('customRoutes',
{
    'logged.search': {
        url: "/search?q",
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'search.html',
            }
        }
    },

    'logged.new-search': {
        url: "/new-search",
        params: {
            type: null,
            q: null
        },
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'new-search.html',
            }
        }
    },

    'logged.search.watch': {
        url: "/watch?v",
        params: {
            meta: null
        },
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'search.watch.html'
            }
        }
    },

    'logged.search.watch.image': {
        url: "/image/{id}",
        params: {
            meta: null
        },
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'watch.image.html'
            }
        }
    },

    'logged.tag.geocode': {
        url: "/tag?v",
        params: {
            meta: null
        },
        views: {
            "loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'tag.geocode.html'
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
                templateUrl: 'admin.html'
            }
        }
    },

    'logged.admin.users': {
        url: "/users",
        views: {
            "admin@logged.admin": {
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

    'logged.admin.archive': {
        url: "/archive",
        views: {
            "admin@logged.admin": {
                dir: 'blueprint',
                templateUrl: 'admin.archive.html'
            }
        }
    }

});

})();
