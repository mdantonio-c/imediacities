import { Observable, of } from "rxjs";
import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";
import { LocalStorageService } from "./local-storage.service";
import { CatalogService } from "./catalog.service";

@Injectable()
export class CatalogServiceStub extends CatalogService {
  constructor() {
    super({} as ApiService, {} as LocalStorageService);
  }
}
