import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { CatalogService, SearchFilter } from "./services/catalog.service";
import { NotificationService } from "@rapydo/services/notification";
import { MediaEntity, Providers } from "./services/data";

@Component({
  selector: "app-catalog",
  templateUrl: "./catalog.component.html",
  styleUrls: ["./catalog.component.css"],
})
export class CatalogComponent implements OnInit {
  loading: boolean = false;
  loadingMapResults: boolean = false;
  totalItems: number = 0;
  results: MediaEntity[];
  countByYears: any;
  countMissingDate: number = 0;
  countByProviders: any;
  currentView: string = "Grid";
  filter: SearchFilter;
  currentPage: number = 1;
  pageSize: number = 12;
  mediaTags: any[];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private catalogService: CatalogService,
    private notify: NotificationService
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      let preset = false;
      if (params["city"]) {
        // preset filter with city value if valid
        let cityCode = params["city"].toUpperCase();
        let p = Providers.filter((provider) => provider.code === cityCode);
        if (p && p.length) {
          this.catalogService.reset(cityCode);
          preset = true;
        }
        // clean the url from the query parameter
        this.router.navigate([], {
          queryParams: { city: null },
          queryParamsHandling: "merge",
        });
      }

      if (!preset) {
        this.catalogService.init();
      }
      this.changeFilter(this.catalogService.filter);
      if ("page" in this.catalogService.filter) {
        this.currentPage = this.catalogService.filter["page"];
      }
    });
  }

  load() {
    this.loading = true;
    // clean current results
    this.results = [];
    this.mediaTags = [];

    let page = this.currentPage;
    if ("page" in this.filter) page = this.filter["page"];

    this.catalogService.search(this.filter, page, this.pageSize).subscribe(
      (response) => {
        this.results = response.data;
        this.totalItems = response.meta.totalItems;
        this.countByYears = response.meta.countByYears;
        this.calculateCountMissingDate();
        this.countByProviders = response.meta.countByProviders;
        this.loading = false;
      },
      (error) => {
        // if (error["filter"]) this.notify.showError(error["filter"]);
        // if (error["match"]) this.notify.showError(error["match"]);
        this.notify.showError(error);
        this.loading = false;
      }
    );
  }

  calculateCountMissingDate() {
    var totalItemsByYears = 0;
    for (let key of Object.keys(this.countByYears)) {
      totalItemsByYears += this.countByYears[key];
    }
    if (this.totalItems > totalItemsByYears) {
      this.countMissingDate = this.totalItems - totalItemsByYears;
    } else {
      this.countMissingDate = 0;
    }
  }

  changeFilter(newFilter: SearchFilter) {
    this.filter = newFilter;
    this.load();
  }

  resetFilter() {
    this.catalogService.reset();
  }

  changePage(page: number) {
    this.currentPage = page;
    this.filter["page"] = page;
    this.load();
  }

  changeView(view) {
    this.currentView = view;
  }

  /**
   * Load relevant media entity for a list of geo tags.
   * @param entityPlaceMap <Map> 'entity-id' => Array<place-id>.
   */
  loadMediaTags(entityPlaceMap) {
    /*console.log(entityPlaceMap);*/
    this.loadingMapResults = true;
    this.catalogService.getRelevantCreations(entityPlaceMap).subscribe(
      (response) => {
        this.mediaTags = response;
        this.loadingMapResults = false;
      },
      (error) => {
        this.notify.showError(
          `Unable to retrieve relevant creations on the map: ${error}`
        );
        this.loadingMapResults = false;
      }
    );
  }
}
