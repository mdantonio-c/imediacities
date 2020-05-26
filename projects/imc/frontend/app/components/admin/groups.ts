
import { Component, ViewChild, TemplateRef, Injector } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '@rapydo/services/api';
import { AuthService } from '@rapydo/services/auth';
import { NotificationService } from '@rapydo/services/notification';
import { FormlyService } from '@rapydo/services/formly'

import { BasePaginationComponent } from '@rapydo/components/base.pagination.component'

export interface Group {

}

@Component({
	selector: 'admin-groups',
	templateUrl: './groups.html'
})
export class AdminGroupsComponent extends BasePaginationComponent<Group> {

	@ViewChild('dataCoordinator', { static: false }) public dataCoordinator: TemplateRef<any>;
	@ViewChild('controlsCell', { static: false }) public controlsCell: TemplateRef<any>;
	@ViewChild('emptyHeader', { static: false }) public emptyHeader: TemplateRef<any>;
	@ViewChild('formModal', { static: false }) public formModal: TemplateRef<any>;

	protected endpoint = 'admin/groups'

	constructor(protected injector: Injector) {

		super(injector);
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
		return this.post(this.endpoint, this.formModal);
	}

	update(row) {
		return this.put(row, this.endpoint, this.formModal);
	}

	submit() {
		this.send(this.endpoint);
	}

}
