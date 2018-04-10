
import { Component } from '@angular/core';

import { ApiService } from '/rapydo/src/app/api.service';
import { NotificationService} from '/rapydo/src/app/app.notification.service';

@Component({
  selector: 'imc-archives-list',
  providers: [ApiService, NotificationService],
  templateUrl: './imc.archives.list.html'
})
export class ArchivesListComponent { 

	private groups: Array<any> = [];

	constructor(private api: ApiService, private notify: NotificationService) {

		this.list();

	}

	list() {
		this.api.get('admin/groups').subscribe(
      		response => {
				this.groups = this.api.parseResponse(response.data);
				this.notify.extractErrors(response, this.notify.WARNING);
			}, error => {
				console.log(error);
      			this.notify.extractErrors(error, this.notify.ERROR);
      		}
       );
	}
}
