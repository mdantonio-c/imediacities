import { Component, OnInit } from '@angular/core';
import { NotificationService } from '/rapydo/src/app/services/notification';
import { Providers } from '../../catalog/services/data';
import { CatalogService } from '../../catalog/services/catalog.service'

@Component({
	selector: 'user-workspace',
	templateUrl: 'user-workspace.html',
	styleUrls: ['./user-workspace.css']
})
export class UserWorkspaceComponent implements OnInit {
	cities: string[] = [];
	city: string = 'Bologna';

	constructor(
		private catalogService: CatalogService,
		private notify: NotificationService) { }

	slides = [
		{ img: "http://placehold.it/350x150/000000" },
		{ img: "http://placehold.it/350x150/111111" },
		{ img: "http://placehold.it/350x150/333333" },
		{ img: "http://placehold.it/350x150/666666" }
	];
	slideConfig = { "slidesToShow": 4, "slidesToScroll": 4 };

	slickInit(e) {
		console.log('slick initialized');
	}

	breakpoint(e) {
		console.log('breakpoint');
	}

	afterChange(e) {
		console.log('afterChange');
	}

	beforeChange(e) {
		console.log('beforeChange');
	}

	ngOnInit() {
		for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
		this.cities = this.cities.sort();
	}

}