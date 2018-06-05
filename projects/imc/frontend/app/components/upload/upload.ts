
import { Component, ViewChild, TemplateRef } from '@angular/core';
import { saveAs as importedSaveAs } from "file-saver";
import { FileSelectDirective, FileDropDirective, FileUploader } from 'ng2-file-upload';
// import { FileSelectDirective, FileDropDirective, FileUploader } from 'ng2-file-upload/ng2-file-upload';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '/rapydo/src/app/services/api';
import { AuthService } from '/rapydo/src/app/services/auth';
import { NotificationService} from '/rapydo/src/app/services/notification';
import { FormlyService } from '/rapydo/src/app/services/formly'

import { BasePaginationComponent } from '/rapydo/src/app/components/base.pagination.component'

const URL = 'https://evening-anchorage-3159.herokuapp.com/api/';
@Component({
  selector: 'upload',
  styles: [
  	'.my-drop-zone { border: dotted 3px lightgray; text-align:center; height: 100px; line-height: 100px;}',
  	'.nv-file-over { border: dotted 3px red; }'
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

	public uploader:FileUploader = new FileUploader({url: URL});
	public hasDropZoneOver:boolean = false;
 
	protected endpoint = 'not_used'

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

	list() {
		return this.get('stage')
	}

	remove(uuid) {
		return this.delete(this.endpoint, uuid);
	}

	download(filename) {

		var options = {
			"rawResponse": true,
			// "conf": {'responseType': ResponseContentType.Blob}
			"conf": {
				'responseType': 'arraybuffer',
				"observe": "response",
			}
		};
		this.api.get('download', filename, {}, options).subscribe(
			response => {
				var contentType = response.headers['content-type'] || 'application/octet-stream';
				console.log(contentType);
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
