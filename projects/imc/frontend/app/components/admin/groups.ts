
import { Component, ViewChild, TemplateRef } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ApiService } from '/rapydo/src/app/services/api';
import { AuthService } from '/rapydo/src/app/services/auth';
import { NotificationService} from '/rapydo/src/app/services/notification';
import { FormlyService } from '/rapydo/src/app/services/formly'

import { BasePaginationComponent } from '/rapydo/src/app/components/base.pagination.component'

@Component({
  selector: 'admin-groups',
  providers: [ApiService, AuthService, NotificationService, FormlyService],
  templateUrl: './groups.html'
})
export class AdminGroupsComponent extends BasePaginationComponent {

	@ViewChild('dataCoordinator') public dataCoordinator: TemplateRef<any>;
	@ViewChild('controlsCell') public controlsCell: TemplateRef<any>;
	@ViewChild('emptyHeader') public emptyHeader: TemplateRef<any>;
	@ViewChild('formModal') public formModal: TemplateRef<any>;

	protected endpoint = 'admin/groups'

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
	        {name: 'Shortname', prop: "shortname", flexGrow: 0.5},
	        {name: 'Fullname', prop: "fullname", flexGrow: 1.5},
	        {name: 'Coordinator', prop: "_coordinator", cellTemplate: this.dataCoordinator, flexGrow: 1.0},
			{name: 'controls', prop: 'controls', cellTemplate: this.controlsCell, headerTemplate: this.emptyHeader, flexGrow: 0.2},
		];
	}

	list() {
		return this.get(this.endpoint)
	}

	remove(uuid) {
		return this.delete(this.endpoint, uuid);
	}

	create() {
		var data = {'get_schema': true, 'autocomplete': false} 

		return this.post(this.endpoint, data, this.formModal);
	}

	update(row) {

		var data = {'get_schema': true, 'autocomplete': false} 

		return this.put(row, this.endpoint, data, this.formModal);
	}

	submit(data) {
		this.send(data, this.endpoint);
	}

}
