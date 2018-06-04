
import { Component, ViewChild, TemplateRef } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '/rapydo/src/app/services/api';
import { AuthService } from '/rapydo/src/app/services/auth';
import { NotificationService} from '/rapydo/src/app/services/notification';
import { FormlyService } from '/rapydo/src/app/services/formly'

import { BasePaginationComponent } from '/rapydo/src/app/components/base.pagination.component'

@Component({
  selector: 'upload',
  providers: [ApiService, AuthService, NotificationService, FormlyService],
  templateUrl: './upload.html'
})
export class UploadComponent extends BasePaginationComponent {

	@ViewChild('dataSize') public dataSize: TemplateRef<any>;
	@ViewChild('dataUploadData') public dataUploadData: TemplateRef<any>;
	@ViewChild('dataStatus') public dataStatus: TemplateRef<any>;
	@ViewChild('controlsCell') public controlsCell: TemplateRef<any>;
	@ViewChild('emptyHeader') public emptyHeader: TemplateRef<any>;

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

	list() {
		return this.get('stage')
	}

	remove(uuid) {
		return this.delete(this.endpoint, uuid);
	}

	download(filename) {
		console.log("Download not implemented");
		console.log(filename);
/*
        var config = {'responseType': 'arraybuffer'};
        ApiService2.get('download/'+filename, "", {}, {"rawResponse": true, "conf": config}).toPromise().then(
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
*/

	}
}
