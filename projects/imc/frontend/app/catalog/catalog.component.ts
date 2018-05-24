import { Component, OnInit } from '@angular/core';
import { CatalogService, SearchFilter } from './services/catalog.service'
import { NotificationService} from '/rapydo/src/app/services/notification';
import { MediaEntity } from './services/data'

@Component({
	selector: 'app-catalog',
	templateUrl: './catalog.component.html'
})
export class CatalogComponent implements OnInit {
	loading: boolean = false;
	totalItems: number = 0;
	results: MediaEntity[];
	countByYears: any;
	currentView: string = 'Grid';
	filter: SearchFilter;
	currentPage: number = 1;
	pageSize: number = 12;

	constructor(private catalogService: CatalogService, private notify: NotificationService) {
		this.filter = {
			searchTerm: null,
			itemType: 'Video',
			terms: [],
			city: null,
			productionYear: null,
			iprstatus: null
		};
	}

	ngOnInit() {
		this.load();

		/*this.countByYears = this.catalogService.countByYears;*/
	}

	load() {
		this.loading = true;
		this.results = this.catalogService.search(this.filter, this.currentPage, this.pageSize).subscribe(
			results => {
				this.results = results.data;
				this.totalItems = this.results.length;
				console.log(this.results);
				this.loading = false;
			},
			error => {
				console.log(error);
      			this.notify.extractErrors(error, this.notify.ERROR);
				this.loading = false;
			});
	}

	changeView(view) {
		this.currentView = view;
	}

}