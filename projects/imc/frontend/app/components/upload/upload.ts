
import { Component, ViewChild, TemplateRef } from '@angular/core';
import { saveAs as importedSaveAs } from "file-saver";
import { FileSelectDirective, FileDropDirective, FileUploader } from 'ng2-file-upload';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '/rapydo/src/app/services/api';
import { AuthService } from '/rapydo/src/app/services/auth';
import { NotificationService} from '/rapydo/src/app/services/notification';
import { FormlyService } from '/rapydo/src/app/services/formly'

import { BasePaginationComponent } from '/rapydo/src/app/components/base.pagination.component'

@Component({
  selector: 'upload',
  styles: [
  	'.my-drop-zone { border: dotted 2px lightgray; text-align:center; height: 100px; line-height: 100px;}',
  	'.nv-file-over { border: dotted 2px red; }'
  ],
  providers: [ApiService, AuthService, NotificationService, FormlyService],
  templateUrl: './upload.html'
})
export class UploadComponent extends BasePaginationComponent {

	@ViewChild('dataSize') public dataSize: TemplateRef<any>;
	@ViewChild('dataUploadData') public dataUploadData: TemplateRef<any>;
	@ViewChild('dataStatus') public dataStatus: TemplateRef<any>;
	@ViewChild('controlsCell') public controlsCell: TemplateRef<any>;
	@ViewChild('emptyHeader') public emptyHeader: TemplateRef<any>;
	public uploader:FileUploader;
	public hasDropZoneOver:boolean = false;
 
	constructor(
		protected api: ApiService,
		protected auth: AuthService,
		protected notify: NotificationService,
		protected modalService: NgbModal,
		protected formly: FormlyService,
		) {

		super("group", api, auth, notify, modalService, formly);

		this.list();
		this.initPaging(20);

/*
		$scope.flowOptions = {
	        target: process.env.apiUrl + '/upload',
	        chunkSize: 10*1024*1024,
	        simultaneousUploads: 1,
	        testChunks: false,
	        permanentErrors: [ 401, 405, 500, 501 ],
	        headers: {Authorization : 'Bearer ' + AuthService2.getToken()}
	    };
*/

		let token = this.auth.getToken();
		this.uploader = new FileUploader(
			{
				url: process.env.apiUrl + '/upload',
				authToken: `Bearer ${token}`,
				disableMultipart: true,
				// authToken: this.auth.getToken()
			}
		);
/*		this.uploader.onAfterAddingFile = (item => {
			console.log(item);	
			// item.withCredentials = false;
		});*/

		this.uploader.onBeforeUploadItem = (item => {
			item.url += "/" + item._file.name;
			// item.withCredentials = false;
		});

		this.uploader.onCompleteItem = (item:any, response:any, status:any, headers:any) => {

			response = JSON.parse(response);
			this.notify.extractErrors(response["Response"], this.notify.ERROR);

			this.list();

		}
	}

	public ngOnInit(): void {

		this.columns = [
	        {name: 'Filename', prop: "name", flexGrow: 2},
	        {name: 'Type', prop: "type", flexGrow: 0.5},
	        {name: 'Size', prop: "size", flexGrow: 0.5, cellTemplate: this.dataSize},
	        {name: 'Upload', prop: "creation", flexGrow: 0.5, cellTemplate: this.dataUploadData},
	        {name: 'Status', prop: "status", flexGrow: 0.5, cellTemplate: this.dataStatus},
			{name: 'controls', prop: 'controls', cellTemplate: this.controlsCell, headerTemplate: this.emptyHeader, flexGrow: 0.2},
		];
	}

	public fileOver(e:any):void {
		this.hasDropZoneOver = e;
	}
/*
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
*/
/*
    self.uploadComplete = function (event, $flow, flowFile) {
    	$rootScope.transitionConfirmationRequested = false;
    	self.loadFiles();
    };
*/
/*
    self.uploadStart = function (event, $flow, flowFile) {
    	$rootScope.transitionConfirmationRequested = true;
    	$rootScope.transitionConfirmationMessage = "Are you sure want to leave this page? This may interrupt your uploads";
    };
*/
	list() {
		return this.get('stage')
	}

	remove(filename: string) {
		return this.delete("stage", filename);
	}

	download(filename) {

		let options = {
			"rawResponse": true,
			// "conf": {'responseType': ResponseContentType.Blob}
			"conf": {
				'responseType': 'arraybuffer',
				"observe": "response",
			}
		};
		this.api.get('download', filename, {}, options).subscribe(
			response => {
				let contentType = response.headers['content-type'] || 'application/octet-stream';
				const blob = new Blob([response.body], { type: contentType });
				importedSaveAs(blob, filename);
				//this.notify.extractErrors(response, this.notify.WARNING);
			},
			error => {
				this.notify.showError('Unable to download file: ' + filename);
			}
		);
	}
}