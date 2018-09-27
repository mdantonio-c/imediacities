import { Component, Input, Output, EventEmitter } from '@angular/core';
import { SearchResultComponent } from "../search-result.component";

@Component({
	selector: 'search-navbar',
	templateUrl: './search-navbar.component.html',
	styleUrls: ['./search-navbar.component.css']
})

export class SearchNavbarComponent extends SearchResultComponent {
	@Input() totalItems: number;
	@Input() loading: boolean;
	displayMode: string = 'Grid';
	@Output() onViewChange: EventEmitter<string> = new EventEmitter<string>();

	ngOnChanges() {}

	changeView(choice) {
		console.log("changeView: user=" + JSON.stringify(this.getUser()));
		this.displayMode = choice;
		this.onViewChange.emit(choice);
	}
}