import { Component } from "@angular/core";
import { NgxSpinnerService } from "ngx-spinner";

import { Group } from "@rapydo/types";
import { ApiService } from "@rapydo/services/api";
import { NotificationService } from "@rapydo/services/notification";

@Component({
  selector: "imc-archives-list",
  templateUrl: "./archives.list.html",
})
export class ArchivesListComponent {
  public groups: Array<Group> = [];

  constructor(
    private api: ApiService,
    private notify: NotificationService,
    private spinner: NgxSpinnerService
  ) {
    this.list();
  }

  list() {
    this.spinner.show();
    this.api
      .get<Group[]>("admin/groups", "", {}, { validationSchema: "Groups" })
      .subscribe(
        (response) => {
          this.groups = response;
          this.spinner.hide();
        },
        (error) => {
          this.notify.showError(error);
          this.spinner.hide();
        }
      );
  }
}
