import { Component, OnInit } from '@angular/core';
import { CatalogService, SearchFilter } from './services/catalog.service'
import { NotificationService } from '/rapydo/src/app/services/notification';
import { MediaEntity } from './services/data'

@Component({
	selector: 'app-catalog',
	templateUrl: './catalog.component.html',
	styleUrls: ['./catalog.component.css']
})
export class CatalogComponent implements OnInit {
	loading: boolean = false;
	loadingMapResults: boolean = false;
	totalItems: number = 0;
	results: MediaEntity[];
	countByYears: any;
	countMissingDate: number = 0;
	countByProviders: any;
	currentView: string = 'Grid';
	filter: SearchFilter;
	currentPage: number = 1;
	pageSize: number = 12;
	mediaTags: any[];

	constructor(
		private catalogService: CatalogService,
		private notify: NotificationService)
	{}	

	ngOnInit() {
		this.catalogService.init();
		this.changeFilter(this.catalogService.filter);
	}

	load() {
		/*console.log(this.filter);*/
		this.loading = true;
		// clean current results
		this.results = [];
		this.mediaTags = [];
		this.catalogService.search(this.filter, this.currentPage, this.pageSize).subscribe(
			response => {
				this.results = response["Response"].data;
				this.totalItems = response["Meta"].totalItems;
				this.countByYears = response["Meta"].countByYears;
				this.calculateCountMissingDate();
				this.countByProviders = response["Meta"].countByProviders;
				this.loading = false;
			},
			error => {
				this.notify.extractErrors(error.error.Response, this.notify.ERROR);
				this.loading = false;
			});
	}

	calculateCountMissingDate() {
		var totalItemsByYears = 0;
		for (let key of Object.keys(this.countByYears)) {
      		totalItemsByYears += this.countByYears[key];
    	}
    	if(this.totalItems > totalItemsByYears){
    		this.countMissingDate = this.totalItems - totalItemsByYears;
    	}else{
    		this.countMissingDate = 0;
    	}
	}

	changeFilter(newFilter: SearchFilter) {
		this.filter = newFilter;
		this.load()
	}

	resetFilter() {
		this.catalogService.reset();	
	}

	changePage(page: number) {
		this.currentPage = page;
		this.load()
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
			response => {
				this.mediaTags = response["Response"].data;
				this.loadingMapResults = false;
			},
			error => {
				this.notify.showError(`Unable to retrieve relevant creations on the map: ${error}`);
				this.loadingMapResults = false;
			});
	}

}