import { Component, OnInit } from '@angular/core';
import { Providers } from '../../catalog/services/data';

@Component({
	selector: 'user-workspace',
	templateUrl: 'user-workspace.html',
	styleUrls: ['./user-workspace.css']
})
export class UserWorkspaceComponent implements OnInit {
	cities: string[] = [];

	ngOnInit() {
		for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
		this.cities = this.cities.sort();
	}

}