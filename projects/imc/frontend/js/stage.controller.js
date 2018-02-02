(function() {
  'use strict';

var app = angular.module('web').controller('StageController', StageController);

// The controller
function StageController($scope, $rootScope, $log, $auth, $q, $window, DataService, FormDialogService, noty, FileSaver)
{
	var self = this;

	self.files = [];

	const globalConfig = require('globalConfig');
	$scope.flowOptions = {
        target: globalConfig.apiUrl + '/upload',
        chunkSize: 10*1024*1024,
        simultaneousUploads: 1,
        testChunks: false,
        permanentErrors: [ 401, 405, 500, 501 ],
        headers: {Authorization : 'Bearer ' + $auth.getToken()}
    };

    self.importStageFiles = function(file) {
		DataService.importStageFiles(file).then(
			function(out_data) {
		    	// console.log(out_data)
		    	self.loadFiles();

	            noty.extractErrors(out_data, noty.WARNING);
			}, function(out_data) {
		    	console.log("error...");

	            noty.extractErrors(out_data, noty.ERROR);
			});
	};
    // flowFile is always undefined, some errors here o in flow-init?
    self.uploadComplete = function (event, $flow, flowFile) {
    	$rootScope.transitionConfirmationRequested = false;
    	self.loadFiles();
    };
    self.uploadStart = function (event, $flow, flowFile) {
    	$rootScope.transitionConfirmationRequested = true;
    	$rootScope.transitionConfirmationMessage = "Are you sure want to leave this page? This may interrupt your uploads";
    };
	self.loading = true;
	self.loadFiles = function() {
		DataService.getStageFiles().then(
			function(out_data) {
				self.files = out_data.data;
				self.loading = false;

	            noty.extractErrors(out_data, noty.WARNING);
			}, function(out_data) {
				self.loading = false;

	            noty.extractErrors(out_data, noty.ERROR);
			});
	};
	self.loadFiles();

	self.deleteFile = function(name, ev) {

		var text = "Are you really sure you want to delete this file?";
		var subtext = "This operation cannot be undone.";
		FormDialogService.showConfirmDialog(text, subtext).then(
			function(answer) {
				DataService.deleteStageFile(name).then(
					function(out_data) {
			    		$log.debug("File removed");
			    		self.loadFiles();
			    		noty.showWarning("File successfully deleted.");
		    		},
		    		function(out_data) {
						noty.extractErrors(out_data, noty.ERROR);
		    		}
	    		);
			},
			function() {

			}
		);
	};
	self.deleteFiles = function(listctrl, ev) {
		var text = "Are you really sure you want to delete selected files?";
		var subtext = "This operation cannot be undone.";
		FormDialogService.showConfirmDialog(text, subtext).then(
			function() {
			
				var promises = [];

				for (var i=0; i<self.files.length; i++) {
					if (!self.files[i].isSelected) continue;

					var promise = DataService.deleteStageFile(self.files[i].name);
					promises.push(promise);

		    	}
		    	listctrl.selectedElements = 0;

				$q.all(promises).then(
					function(out_data) {
		        		$log.debug("Files removed");
		        		self.loadFiles();
		        		noty.extractErrors(out_data, noty.WARNINGS);
		    		},
		    		function(out_data) {
		        		noty.extractErrors(out_data, noty.ERROR);
		    		}
		    	);

			}, function() {
			}
		);
	};
	self.downloadFile = function(name) {
		DataService.downloadStageFile(name).then(
			function(out_data) {
				var headers = out_data.headers();
				var contentType = headers['content-type'] || 'application/octet-stream';
				//console.log('content-type: ' + contentType);
				var data = new Blob([out_data.data], { type: contentType });
				FileSaver.saveAs(data, name);

	            noty.extractErrors(out_data, noty.WARNING);
			}, function(out_data) {
				// self.loading = false;
	            noty.extractErrors(out_data, noty.ERROR);
			});
	};
	
}


})();