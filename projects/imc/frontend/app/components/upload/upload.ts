import { Component, ViewChild, TemplateRef, Injector } from "@angular/core";
import { HttpResponse } from "@angular/common/http";
import { Observable } from "rxjs";
import { saveAs as importedSaveAs } from "file-saver";
import { UploadxOptions, UploadState, UploadxService } from "ngx-uploadx";
import { NgbModal } from "@ng-bootstrap/ng-bootstrap";

import { ApiService } from "@rapydo/services/api";
import { AuthService } from "@rapydo/services/auth";
import { NotificationService } from "@rapydo/services/notification";
import { FormlyService } from "@rapydo/services/formly";

import { BasePaginationComponent } from "@rapydo/components/base.pagination.component";

import { environment } from "@rapydo/../environments/environment";
import { StageService } from "../../services/stage.service";

export interface Data {}

@Component({
  selector: "upload",
  templateUrl: "./upload.html",
})
export class UploadComponent extends BasePaginationComponent<Data> {
  @ViewChild("dataSize", { static: false }) public dataSize: TemplateRef<any>;
  @ViewChild("dataUploadData", { static: false })
  public dataUploadData: TemplateRef<any>;
  @ViewChild("dataStatus", { static: false }) public dataStatus: TemplateRef<
    any
  >;
  @ViewChild("controlsCell", { static: false })
  public controlsCell: TemplateRef<any>;
  @ViewChild("emptyHeader", { static: false }) public emptyHeader: TemplateRef<
    any
  >;

  public upload_options: any;
  public upload_progress: any = {};
  public upload_endpoint: string;

  constructor(
    protected injector: Injector,
    private uploadService: UploadxService,
    private stageService: StageService
  ) {
    super(injector);
    this.init("file", "stage", null);
    this.initPaging(50, true);
    this.list();
  }

  public ngOnInit(): void {
    this.upload_endpoint = environment.backendURI + "/api/upload";

    this.upload_options = {
      endpoint: this.upload_endpoint,
      token: this.auth.getToken(),
      // allowedTypes: 'image/*',
      // "application/x-zip-compressed,application/x-compressed,application/zip,multipart/x-zip",
      multiple2: true,
      autoUpload: true,
    };

    this.uploadService.connect(this.upload_options).subscribe((response) => {
      if (response && response.length > 0) {
        // Show Error from last response
        let resp = response[response.length - 1];
        if (resp.response) {
          if (resp.responseStatus == 200) {
            console.log(resp.response);
            this.notify.showSuccess(
              // "Upload completed: " + resp.response.filename
              "Upload completed: " + resp.response
            );
          } else {
            this.notify.showError(resp.response);
          }
        }
      }
    });
  }

  public ngAfterViewInit(): void {
    this.columns = [
      { name: "Filename", prop: "name", flexGrow: 2 },
      { name: "Type", prop: "type", flexGrow: 0.5 },
      {
        name: "Size",
        prop: "size",
        flexGrow: 0.5,
        cellTemplate: this.dataSize,
      },
      {
        name: "Upload",
        prop: "creation",
        flexGrow: 0.5,
        cellTemplate: this.dataUploadData,
      },
      {
        name: "Status",
        prop: "status",
        flexGrow: 0.5,
        cellTemplate: this.dataStatus,
      },
      {
        name: "controls",
        prop: "controls",
        cellTemplate: this.controlsCell,
        headerTemplate: this.emptyHeader,
        flexGrow: 0.4,
      },
    ];
  }

  onUpload(state: Observable<UploadState>) {
    state.subscribe((item: UploadState) => {
      if (item.progress > 0) {
        this.upload_progress[item.name] = item.progress;
      } else {
        // set 0 also in case of null and undefined
        this.upload_progress[item.name] = 0;
      }
      if (
        item.progress == 100 &&
        item.remaining == 0 &&
        item.status == "complete"
      ) {
        this.list();
        delete this.upload_progress[item.name];
      }
    });
  }

  download(filename) {
    let options = {
      conf: {
        responseType: "arraybuffer",
        observe: "response",
      },
    };
    this.api
      .get<HttpResponse<ArrayBuffer>>("download", filename, {}, options)
      .subscribe(
        (response) => {
          let contentType =
            response.headers["content-type"] || "application/octet-stream";
          const blob = new Blob([response.body], { type: contentType });
          importedSaveAs(blob, filename);
        },
        (error) => {
          this.notify.showError("Unable to download file: " + filename);
        }
      );
  }

  stage(filename) {
    this.stageService.stage(filename).subscribe(
      (resp) => {
        console.log(resp.response);
        this.notify.showSuccess("File staged successfully");
      },
      (error) => {
        this.notify.showCritical(error, `Unable to stage file ${filename}`);
      }
    );
  }
}
