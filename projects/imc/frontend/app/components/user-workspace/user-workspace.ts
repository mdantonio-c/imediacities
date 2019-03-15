import { Component, OnInit } from '@angular/core';
import { NotificationService } from '/rapydo/src/app/services/notification';
import { Providers } from '../../catalog/services/data';
import { CatalogService, SearchFilter } from '../../catalog/services/catalog.service'

@Component({
	selector: 'user-workspace',
	templateUrl: 'user-workspace.html',
	styleUrls: ['./user-workspace.css']
})
export class UserWorkspaceComponent implements OnInit {

	cities: string[] = [];
	selectedCity: string = "Bologna";
	cityFilter: SearchFilter = { city: this.selectedCity };
	countCityResults: number = 0;

	onCityChange(newValue) {
		this.selectedCity = newValue;
		this.cityFilter = { city: newValue };
	}

	countChangedHandler(newCount) {
		this.countCityResults = newCount;
	}

	constructor(
		private catalogService: CatalogService,
		private notify: NotificationService) { }

	ngOnInit() {
		for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
    	this.cities = this.cities.sort();
	}
}