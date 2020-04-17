
import { Component, ViewChild, TemplateRef, Injector } from '@angular/core';
import { Observable } from 'rxjs';
import { saveAs as importedSaveAs } from "file-saver";
import { UploadxOptions, UploadState, UploadxService } from 'ngx-uploadx';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '@rapydo/services/api';
import { AuthService } from '@rapydo/services/auth';
import { NotificationService} from '@rapydo/services/notification';
import { FormlyService } from '@rapydo/services/formly'

import { BasePaginationComponent } from '@rapydo/components/base.pagination.component'

import { environment } from '@rapydo/../environments/environment';

export interface Data {

}

@Component({
  selector: 'upload',
  styles: [
  	'.my-drop-zone { border: dotted 2px lightgray; text-align:center; height: 100px; line-height: 100px;}',
  	'.nv-file-over { border: dotted 2px red; }'
  ],
  templateUrl: './upload.html'
})
export class UploadComponent extends BasePaginationComponent<Data> {

	@ViewChild('dataSize', { static: false }) public dataSize: TemplateRef<any>;
	@ViewChild('dataUploadData', { static: false }) public dataUploadData: TemplateRef<any>;
	@ViewChild('dataStatus', { static: false }) public dataStatus: TemplateRef<any>;
	@ViewChild('controlsCell', { static: false }) public controlsCell: TemplateRef<any>;
	@ViewChild('emptyHeader', { static: false }) public emptyHeader: TemplateRef<any>;

	public upload_options :any;
	public upload_progress: any = {};
	/*
	public allowedMimeType:any = [
		'application/x-zip-compressed',
		'application/x-compressed',
		'application/zip',
		'multipart/x-zip'
	];
	*/
	// public maxFileSize:number = 200*1024*1024; // 200 MB

	public upload_endpoint:string;

	constructor(protected injector: Injector, private uploadService: UploadxService) {

		super(injector);
		this.init("file");

		this.server_side_pagination = true;
		this.endpoint = 'stage';
		this.counter_endpoint = 'stage';
		this.initPaging(50);
		this.list();
	}

	public ngOnInit(): void {

		this.upload_endpoint = environment.apiUrl + '/upload';

		this.upload_options = {
			endpoint: this.upload_endpoint,
			token: this.auth.getToken(),
			allowedTypes: 'application/x-zip-compressed,application/x-compressed,application/zip,multipart/x-zip',
			multiple2: true,
			autoUpload: true
		}
        
		this.uploadService.connect(this.upload_options).subscribe(
			response => {
				if (response && response.length > 0) {
					// Show Error from last response
					let resp = response[response.length-1];
					if (resp.response) {
						if (resp.responseStatus == 200) {
							this.notify.showSuccess("Upload completed: " + resp.response.filename);
						} else {
							this.notify.showError(resp.response);
						}
					}
				}
			}
		);
	}
	public ngAfterViewInit(): void {

		this.columns = [
	        {name: 'Filename', prop: "name", flexGrow: 2},
	        {name: 'Type', prop: "type", flexGrow: 0.5},
	        {name: 'Size', prop: "size", flexGrow: 0.5, cellTemplate: this.dataSize},
	        {name: 'Upload', prop: "creation", flexGrow: 0.5, cellTemplate: this.dataUploadData},
	        {name: 'Status', prop: "status", flexGrow: 0.5, cellTemplate: this.dataStatus},
			{name: 'controls', prop: 'controls', cellTemplate: this.controlsCell, headerTemplate: this.emptyHeader, flexGrow: 0.2},
		];
	}

	onUpload(state: Observable<UploadState>) {
	    state.subscribe((item: UploadState) => {

	    	if (item.progress > 0) {
	    		this.upload_progress[item.name] = item.progress;
	    	} else {
	    		// set 0 also in case of null and undefined
	    		this.upload_progress[item.name] = 0;
	    	}
			if (item.progress == 100 && item.remaining == 0 && item.status == 'complete') {
				this.list();
				delete this.upload_progress[item.name];
			}
	    });
	}

	list() {
		return this.get(this.endpoint);
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
			},
			error => {
				this.notify.showError('Unable to download file: ' + filename);
			}
		);
	}
}
