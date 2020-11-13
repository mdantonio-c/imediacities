import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";
import { Observable, of } from "rxjs";
import * as moment from "moment";

@Injectable()
export class StageService {
  constructor(private api: ApiService) {}

  stage(filename: string) {
    return this.api.post("stage", {
      filename: filename,
      mode: "fast",
    });
  }
}
