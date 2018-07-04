
import { Component } from '@angular/core';

import { ApiService } from '/rapydo/src/app/services/api';
import { NotificationService} from '/rapydo/src/app/services/notification';

@Component({
  selector: 'imc-archives-list',
  providers: [ApiService, NotificationService],
  templateUrl: './archives.list.html'
})
export class ArchivesListComponent { 

	private loading:boolean = false;
	private groups: Array<any> = [];

	constructor(private api: ApiService, private notify: NotificationService) {

		this.list();

	}

	list() {
		this.loading = true;
		this.api.get('admin/groups').subscribe(
      		response => {
				this.groups = this.api.parseResponse(response.data);
				this.notify.extractErrors(response, this.notify.WARNING);
				this.loading = false;
			}, error => {
				console.log(error);
      			this.notify.extractErrors(error, this.notify.ERROR);
      			this.loading = false;
      		}
       );
	}
}
