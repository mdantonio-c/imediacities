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
	countByProviders: any;
	currentView: string = 'Grid';
	filter: SearchFilter;
	currentPage: number = 1;
	pageSize: number = 12;
	mediaTags: any[];

	constructor(private catalogService: CatalogService, private notify: NotificationService) {
		this.filter = {
			searchTerm: null,
			itemType: 'video',
			terms: [],
			provider: null,
			country: null,
			productionYearFrom: 1890,
			productionYearTo: 1999,
			iprstatus: null
		};
	}

	ngOnInit() {
		this.load();
	}

	load() {
		/*console.log(this.filter);*/
		this.loading = true;
		// clean current results
		this.results = [];
		this.catalogService.search(this.filter, this.currentPage, this.pageSize).subscribe(
			response => {
				this.results = response["Response"].data;
				this.totalItems = response["Meta"].totalItems;
				this.countByYears = response["Meta"].countByYears;
				this.countByProviders = response["Meta"].countByProviders;
				this.loading = false;
			},
			error => {
				this.notify.extractErrors(error, this.notify.ERROR);
				this.loading = false;
			});
	}

	changeFilter(newFilter: SearchFilter) {
		this.filter = newFilter;
		this.load()
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
				this.notify.extractErrors(`Unable to retrieve relevant creations on the map: ${error}`, this.notify.ERROR);
				this.loadingMapResults = false;
			});
	}

}