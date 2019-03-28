
import { Component, OnInit, Input, ViewChild, TemplateRef } from '@angular/core';

import { ApiService } from '/rapydo/src/app/services/api';
import { NotificationService} from '/rapydo/src/app/services/notification';

@Component({
  selector: 'imc-archive',
  providers: [ApiService, NotificationService],
  templateUrl: './archive.html'
})
export class ArchiveComponent implements OnInit { 

	@Input() private group: any;
	@ViewChild('dataSize') public dataSize: TemplateRef<any>;
	@ViewChild('dataModification') public dataModification: TemplateRef<any>;
	@ViewChild('dataStatus') public dataStatus: TemplateRef<any>;

	private loading:boolean = false;
	private data: Array<any> = [];
	private rows: Array<any> = [];
	private columns: Array<any> = []
	private page:number = 1;
	private itemsPerPage:number = 10;
	private numPages:number = 1;
	private dataLength:number = 0;

	constructor(private api: ApiService, private notify: NotificationService) {}

	public ngOnInit(): void {

		this.list();

		this.columns = [
	        {name: 'Filename', prop: "name"},
	        {name: 'Type', prop: "type"},
	        {name: 'Size', prop: "size", cellTemplate: this.dataSize},
	        {name: 'Uploaded', prop: "modification", cellTemplate: this.dataModification},
	        {name: 'Status', prop: "status", cellTemplate: this.dataStatus},
		];
	}

	list() {

		this.loading = true;
		let data = {
			"currentpage": 1,
			"perpage": 100000
		}
		this.api.get('stage', this.group.id, data).subscribe(
      		response => {

				this.data = this.api.parseResponse(response.data);
				this.dataLength = this.data.length;
				this.numPages = Math.ceil(this.dataLength / this.itemsPerPage);
				this.rows = this.changePage(this.data);
				this.notify.extractErrors(response, this.notify.WARNING);
				this.loading = false;
			}, error => {
				console.log(error);
      			this.notify.extractErrors(error, this.notify.ERROR);
				this.loading = false;
      		}
  		);

	}

	changePage(data:Array<any>): Array<any> {
		let start = (this.page - 1) * this.itemsPerPage;
		let end = this.itemsPerPage > -1 ? (start + this.itemsPerPage): data.length;
		return data.slice(start, end);
	}

	setPage(page:any) {
		this.page = page;
		this.rows = this.changePage(this.data);
	}
}
