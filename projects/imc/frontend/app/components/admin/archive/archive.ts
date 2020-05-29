import { Component, OnInit, Input, ViewChild, TemplateRef, ChangeDetectionStrategy } from '@angular/core';
import { NgxSpinnerService } from "ngx-spinner";

import { ApiService } from '@rapydo/services/api';
import { NotificationService } from '@rapydo/services/notification';

@Component({
	selector: 'imc-archive',
	templateUrl: './archive.html',
	changeDetection: ChangeDetectionStrategy.OnPush
})
export class ArchiveComponent implements OnInit {

	@Input() public group: any;
	@ViewChild('dataSize', { static: false }) public dataSize: TemplateRef<any>;
	@ViewChild('dataModification', { static: false }) public dataModification: TemplateRef<any>;
	@ViewChild('dataStatus', { static: false }) public dataStatus: TemplateRef<any>;

	private data: Array<any> = [];
	private numPages: number = 1;
	public rows: Array<any> = [];
	public columns: Array<any> = []
	public page: number = 1;
	public itemsPerPage: number = 10;
	public dataLength: number = 0;
	// public loading: boolean = false;

	constructor(
		private api: ApiService,
		private notify: NotificationService,
		private spinner: NgxSpinnerService
	) { }

	ngOnInit(): void {
		this.list();
	}

	ngAfterViewInit(): void {
		this.columns = [
			{ name: 'Filename', prop: "name" },
			{ name: 'Type', prop: "type" },
			{ name: 'Size', prop: "size", cellTemplate: this.dataSize },
			{ name: 'Uploaded', prop: "modification", cellTemplate: this.dataModification },
			{ name: 'Status', prop: "status", cellTemplate: this.dataStatus },
		];
	}

	list() {
		// this.loading = true;
		this.spinner.show(this.group.id);
		let data = {
			"page": 1,
			"size": 100000
		}
		this.api.get('stage', this.group.id, data).subscribe(
			response => {
				this.data = response;
				this.dataLength = this.data.length;
				this.numPages = Math.ceil(this.dataLength / this.itemsPerPage);
				this.rows = this.changePage(this.data);
				// this.loading = false;
				this.spinner.hide(this.group.id);
			}, error => {
				this.notify.showError(error);
				// this.loading = false;
				this.spinner.hide(this.group.id);
			}
		);
	}

	changePage(data: Array<any>): Array<any> {
		let start = (this.page - 1) * this.itemsPerPage;
		let end = this.itemsPerPage > -1 ? (start + this.itemsPerPage) : data.length;
		return data.slice(start, end);
	}

	setPage(page: any) {
		this.page = page;
		this.rows = this.changePage(this.data);
	}
}
