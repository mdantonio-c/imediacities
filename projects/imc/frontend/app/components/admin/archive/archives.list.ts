import { Component } from "@angular/core";
import { NgxSpinnerService } from "ngx-spinner";

import { ApiService } from "@rapydo/services/api";
import { NotificationService } from "@rapydo/services/notification";

@Component({
  selector: "imc-archives-list",
  templateUrl: "./archives.list.html",
})
export class ArchivesListComponent {
  // public loading: boolean = false;
  public groups: Array<any> = [];

  constructor(
    private api: ApiService,
    private notify: NotificationService,
    private spinner: NgxSpinnerService
  ) {
    this.list();
  }

  list() {
    // this.loading = true;
    this.spinner.show();
    this.api.get("admin/groups").subscribe(
      (response) => {
        this.groups = response;
        // this.loading = false;
        this.spinner.hide();
      },
      (error) => {
        this.notify.showError(error);
        // this.loading = false;
        this.spinner.hide();
      }
    );
  }
}
