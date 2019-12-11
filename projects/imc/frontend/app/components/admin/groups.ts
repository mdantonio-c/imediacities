
import { Component, ViewChild, TemplateRef, ChangeDetectorRef } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '@rapydo/services/api';
import { AuthService } from '@rapydo/services/auth';
import { NotificationService } from '@rapydo/services/notification';
import { FormlyService } from '@rapydo/services/formly'

import { BasePaginationComponent } from '@rapydo/components/base.pagination.component'

@Component({
	selector: 'admin-groups',
	providers: [ApiService, AuthService, NotificationService, FormlyService],
	templateUrl: './groups.html'
})
export class AdminGroupsComponent extends BasePaginationComponent {

	@ViewChild('dataCoordinator', { static: false }) public dataCoordinator: TemplateRef<any>;
	@ViewChild('controlsCell', { static: false }) public controlsCell: TemplateRef<any>;
	@ViewChild('emptyHeader', { static: false }) public emptyHeader: TemplateRef<any>;
	@ViewChild('formModal', { static: false }) public formModal: TemplateRef<any>;

	protected endpoint = 'admin/groups'

	constructor(
		protected api: ApiService,
		protected auth: AuthService,
		protected notify: NotificationService,
		protected modalService: NgbModal,
		protected formly: FormlyService,
		protected changeDetectorRef: ChangeDetectorRef
	) {

		super(api, auth, notify, modalService, formly, changeDetectorRef);
		this.init("group");

		this.list();
		this.initPaging(20);
	}

	ngOnInit(): void { }

	ngAfterViewInit(): void {

		this.columns = [
			{ name: 'Shortname', prop: "shortname", flexGrow: 0.5 },
			{ name: 'Fullname', prop: "fullname", flexGrow: 1.5 },
			{ name: 'Coordinator', prop: "_coordinator", cellTemplate: this.dataCoordinator, flexGrow: 1.0 },
			{ name: 'controls', prop: 'controls', cellTemplate: this.controlsCell, headerTemplate: this.emptyHeader, flexGrow: 0.2 },
		];
	}

	list() {
		return this.get(this.endpoint)
	}

	remove(uuid) {
		return this.delete(this.endpoint, uuid);
	}

	create() {
		let data = { 'get_schema': true, 'autocomplete': false }

		return this.post(this.endpoint, data, this.formModal, false);
	}

	update(row) {

		let data = { 'get_schema': true, 'autocomplete': false }

		return this.put(row, this.endpoint, data, this.formModal, false);
	}

	submit() {
		this.send(this.endpoint);
	}

}
