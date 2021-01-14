import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";
import { Observable, of } from "rxjs";
import { MediaEntity, Providers } from "./data";
import { LocalStorageService } from "./local-storage.service";
import { SearchResponse, GeoDistanceAnnotation } from "@app/types";

export interface SearchFilter {
  searchTerm?: string;
  itemType?: string;
  terms?: SearchTerm[];
  provider?: string;
  city?: string;
  country?: string;
  productionYearFrom?: number;
  productionYearTo?: number;
  iprstatus?: string;
  missingDate?: boolean;
  annotated_by?: AnnotatedByFilter;
}

export interface AnnotatedByFilter {
  user: string;
  type: string;
}

export interface SearchTerm {
  iri?: string;
  label: string;
}

const matchFields = ["title", "contributor", "keyword", "description"];

@Injectable()
export class CatalogService {
  private _data: MediaEntity[] = [];
  private _countByYears: any;
  private _countByProviders: any;
  private _filter: SearchFilter;

  constructor(
    private api: ApiService,
    private localStorageService: LocalStorageService
  ) {}

  get filter() {
    return this._filter;
  }

  init() {
    this._filter = this.localStorageService.get("filter", {
      searchTerm: null,
      itemType: "all",
      terms: [],
      provider: null,
      city: null,
      country: null,
      productionYearFrom: 1890,
      productionYearTo: 1999,
      iprstatus: null,
      missingDate: true,
    });
  }

  /**
   * Search for media entities from the catalog.
   * @param filter
   * @param pageIdx
   * @param pageSize
   */
  search(
    filter: SearchFilter,
    pageIdx: number,
    pageSize: number,
    cached: boolean = true
  ): Observable<SearchResponse> {
    // let endpoint = "search?page=" + pageIdx + "&size=" + pageSize;
    this._filter = filter;
    let data = {
      match: null,
      filter: {
        type: filter.itemType,
        provider: filter.provider,
        city: filter.city,
        iprstatus: filter.iprstatus,
        yearfrom: filter.productionYearFrom,
        yearto: filter.productionYearTo,
        terms: filter.terms,
        missingDate: filter.missingDate,
      },
      page: pageId,
      size: pageSize,
    };
    // FIXME: the following filter has no effect without an authentication token
    if (filter.annotated_by) {
      data.filter["annotated_by"] = filter.annotated_by;
    }
    if (filter.searchTerm) {
      data.match = { term: filter.searchTerm, fields: matchFields };
    }
    if (cached) this.cacheValues();
    return this.api.post("search", data);
  }

  /**
   * Look for get-tags.
   * @param pin
   * @param distance
   * @param cFilter
   */
  getGeoDistanceAnnotations(
    pin,
    distance,
    filter
  ): Observable<GeoDistanceAnnotation[]> {
    let data = {
      filter: {
        type: "TAG",
        geo_distance: {
          distance: distance,
          location: {
            lat: pin[0],
            long: pin[1],
          },
        },
        creation: null,
      },
    };
    // setup filter for media entities
    if (filter !== undefined) {
      let creation = {
        match: null,
        filter: {
          type: filter.itemType,
          provider: filter.provider,
          city: filter.city,
          terms: filter.terms,
          iprstatus: filter.iprstatus,
          yearfrom: filter.productionYearFrom,
          yearto: filter.productionYearTo,
          missingDate: filter.missingDate,
        },
      };
      if (filter.searchTerm) {
        creation.match = { term: filter.searchTerm, fields: matchFields };
      }
      data.filter.creation = creation;
    }
    return this.api.post("annotations/search", data);
  }

  /**
   * Retrieve a list of relevant creations for given creation uuids and related place ids.
   * @param relevantCreations
   */
  getRelevantCreations = function (relevantCreations) {
    if (relevantCreations === undefined || relevantCreations.size === 0) {
      return of([]);
    }
    let data = {
      "relevant-list": [],
    };
    for (let entry of Array.from(relevantCreations.entries())) {
      let item = {
        "creation-id": entry[0],
        "place-ids": Array.from(entry[1]),
      };
      data["relevant-list"].push(item);
    }
    return this.api.post("search_place", data);
  };

  getProviderPosition(provider: string) {
    for (let p of Providers) {
      if (p.code === provider) {
        return p.city.position;
      }
    }
  }

  getProviderCity(provider: string) {
    for (let p of Providers) {
      if (p.code === provider) {
        return p.city;
      }
    }
  }

  private providerToCity(provider) {
    let c = null;
    if (provider === "TTE") {
      c = "Athens";
    } else if (provider === "CCB") {
      c = "Bologna";
    } else if (provider === "CRB") {
      c = "Brussels";
    } else if (provider === "DFI") {
      c = "Copenhagen";
    } else if (provider === "DIF") {
      c = "Frankfurt";
    } else if (provider === "FDC") {
      c = "Barcelona";
    } else if (provider === "MNC") {
      c = "Turin";
    } else if (provider === "OFM") {
      c = "Vienna";
    } else if (provider === "WSTLA") {
      c = "Vienna";
    } else if (provider === "SFI") {
      c = "Stockholm";
    }
    return c;
  }

  reset(provider?: string) {
    let city = null;
    if (provider) {
      city = this.providerToCity(provider);
    }
    this._filter = {
      searchTerm: null,
      itemType: "all",
      terms: [],
      provider: provider || null,
      city: city,
      country: null,
      productionYearFrom: 1890,
      productionYearTo: 1999,
      iprstatus: null,
      missingDate: true,
    };
    this.cacheValues();
  }

  private cacheValues() {
    this.localStorageService.set("filter", this.filter);
  }
}
