(function() {
  'use strict';

angular.module('web').controller('UploadController', UploadController);

function UploadController($scope, $log, $auth, noty)
{
	var self = this;

	$scope.flowOptions = {
        target: apiUrl + '/upload',
        testChunks: false,
        permanentErrors: [ 401, 405, 500, 501 ],
        // withCredentials: true,
        headers: {Authorization : 'Bearer ' + $auth.getToken()}
    }
}

})();