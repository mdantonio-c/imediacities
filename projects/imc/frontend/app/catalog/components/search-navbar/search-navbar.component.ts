import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
	selector: 'search-navbar',
	templateUrl: './search-navbar.component.html',
	styleUrls: ['./search-navbar.component.css']
})
export class SearchNavbarComponent {
	@Input() totalItems: number;
	@Input() loading: boolean;
	displayMode: string = 'Grid';
	@Output() onViewChange: EventEmitter<string> = new EventEmitter<string>();

	changeView(choice) {
		this.displayMode = choice;
		this.onViewChange.emit(choice);
	}
}