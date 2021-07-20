import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";

@Injectable()
export class StageService {
  constructor(private api: ApiService) {}

  stage(filename: string) {
    return this.api.post("/api/stage", {
      filename: filename,
      mode: "fast",
    });
  }
}
