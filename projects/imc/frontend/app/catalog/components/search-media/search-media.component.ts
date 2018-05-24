import { Component, Input, OnInit } from '@angular/core';

@Component({
	selector: 'search-media',
	templateUrl: './search-media.component.html'
})
export class SearchMediaComponent implements OnInit {
	@Input() media;

	constructor() { }

	ngOnInit() {
	}

}