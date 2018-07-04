(function() {
  'use strict';

var app = angular.module('web').controller('ArchiveController', ArchiveController);

// The controller
function ArchiveController($log, $q, DataService, FormDialogService, noty)
{
	var self = this;
	self.files = [];

	self.loadAll = function() {
		self.loading = true;
		self.groups = [];
		DataService.getGroups().then(
			function(out_data) {
				self.groups = out_data.data;
				for (var i=0; i<self.groups.length; i++) {
					var group_id = self.groups[i].id;
					self.loadFiles(group_id);
				}
				self.loading = false;
				noty.extractErrors(out_data, noty.WARNING);
			},
			function(out_data) {
				self.loading = false;
				noty.extractErrors(out_data, noty.ERROR);
			}
		);
	};

	self.loadFiles = function(group) {
		DataService.getStageFiles(group).then(
			function(out_data) {
				self.files[group] = out_data.data;

	            // noty.extractErrors(out_data, noty.WARNING);
			}, function(out_data) {

	            noty.extractErrors(out_data, noty.ERROR);
			});
	};

	self.loadAll();

	// self.loadFiles();

	// self.deleteFile = function(name, ev) {

	// 	var text = "Are you really sure you want to delete this file?";
	// 	var subtext = "This operation cannot be undone.";
	// 	FormDialogService.showConfirmDialog(text, subtext).then(
	// 		function(answer) {
	// 			DataService.deleteStageFile(name).then(
	// 				function(out_data) {
	// 		    		$log.debug("File removed");
	// 		    		self.loadFiles();
	// 		    		noty.showWarning("File successfully deleted.");
	// 	    		},
	// 	    		function(out_data) {
	// 					noty.extractErrors(out_data, noty.ERROR);
	// 	    		}
	//     		);
	// 		},
	// 		function() {

	// 		}
	// 	);
	// }

	// self.deleteFiles = function(listctrl, ev) {
	// 	var text = "Are you really sure you want to delete selected files?";
	// 	var subtext = "This operation cannot be undone.";
	// 	FormDialogService.showConfirmDialog(text, subtext).then(
	// 		function() {
			
	// 			var promises = [];

	// 			for (var i=0; i<self.files.length; i++) {
	// 				if (!self.files[i].isSelected) continue;

	// 				var promise = DataService.deleteStageFile(self.files[i].name);
	// 				promises.push(promise)

	// 	    	}
	// 	    	listctrl.selectedElements = 0;

	// 			$q.all(promises).then(
	// 				function(out_data) {
	// 	        		$log.debug("Files removed");
	// 	        		self.loadFiles();
	// 	        		noty.extractErrors(out_data, noty.WARNINGS);
	// 	    		},
	// 	    		function(out_data) {
	// 	        		noty.extractErrors(out_data, noty.ERROR);
	// 	    		}
	// 	    	);

	// 		}, function() {
	// 		}
	// 	);
	// }

}

ArchiveController.$inject = [
	"$log", "$q", "DataService", "FormDialogService", "noty"
];


})();