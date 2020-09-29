import {
  Component,
  OnInit,
  Input,
  ViewChild,
  TemplateRef,
  ChangeDetectionStrategy,
} from "@angular/core";
import { NgxSpinnerService } from "ngx-spinner";

import { ApiService } from "@rapydo/services/api";
import { NotificationService } from "@rapydo/services/notification";

import { Group } from "@rapydo/types";
import { File } from "@app/types";

@Component({
  selector: "imc-archive",
  templateUrl: "./archive.html",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArchiveComponent implements OnInit {
  @Input() public group: Group;
  @ViewChild("dataSize", { static: false }) public dataSize: TemplateRef<any>;
  @ViewChild("dataModification", { static: false })
  public dataModification: TemplateRef<any>;
  @ViewChild("dataStatus", { static: false }) public dataStatus: TemplateRef<
    any
  >;

  private data: Array<File> = [];
  private numPages: number = 1;
  public rows: Array<File> = [];
  public columns: Array<any> = [];
  public page: number = 1;
  public itemsPerPage: number = 10;
  public dataLength: number = 0;

  constructor(
    private api: ApiService,
    private notify: NotificationService,
    private spinner: NgxSpinnerService
  ) {}

  ngOnInit(): void {
    this.list();
  }

  ngAfterViewInit(): void {
    this.columns = [
      { name: "Filename", prop: "name" },
      { name: "Type", prop: "type" },
      { name: "Size", prop: "size", cellTemplate: this.dataSize },
      {
        name: "Uploaded",
        prop: "modification",
        cellTemplate: this.dataModification,
      },
      { name: "Status", prop: "status", cellTemplate: this.dataStatus },
    ];
  }

  list() {
    this.spinner.show(this.group.uuid);
    let data = {
      page: 1,
      size: 100,
    };
    this.api
      .get<File[]>("stage/" + this.group.uuid, "", data, {
        validationSchema: "Files",
      })
      .subscribe(
        (response) => {
          this.data = response;
          this.dataLength = this.data.length;
          this.numPages = Math.ceil(this.dataLength / this.itemsPerPage);
          this.rows = this.changePage(this.data);
          this.spinner.hide(this.group.uuid);
        },
        (error) => {
          this.notify.showError(error);
          this.spinner.hide(this.group.uuid);
        }
      );
  }

  changePage(data: Array<File>): Array<File> {
    let start = (this.page - 1) * this.itemsPerPage;
    let end = this.itemsPerPage > -1 ? start + this.itemsPerPage : data.length;
    return data.slice(start, end);
  }

  setPage(page: number) {
    this.page = page;
    this.rows = this.changePage(this.data);
  }
}
