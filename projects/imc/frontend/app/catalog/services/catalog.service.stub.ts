import { Observable, of } from "rxjs";
import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";
import { LocalStorageService } from "./local-storage.service";
import {
  CatalogService,
  SearchFilter,
  YEAR_FROM,
  YEAR_TO,
} from "./catalog.service";
import { SearchResponse } from "../../types";
import { SEARCH_RESPONSE } from "./data.mock";

@Injectable()
export class CatalogServiceStub extends CatalogService {
  constructor() {
    super({} as ApiService, {} as LocalStorageService);
  }

  init() {
    this._filter = {
      searchTerm: null,
      itemType: "all",
      terms: [],
      provider: null,
      city: null,
      country: null,
      productionYearFrom: YEAR_FROM,
      productionYearTo: YEAR_TO,
      iprstatus: null,
      missingDate: true,
    };
  }

  reset(provider?: string) {
    // TODO
  }

  search(
    filter: SearchFilter,
    pageIdx: number,
    pageSize: number,
    cached: boolean = true
  ): Observable<SearchResponse> {
    return of(SEARCH_RESPONSE);
  }
}
