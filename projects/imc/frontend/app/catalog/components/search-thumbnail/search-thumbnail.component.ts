import { Component, Input, OnInit } from '@angular/core';

@Component({
	selector: 'search-thumbnail',
	templateUrl: './search-thumbnail.component.html'
})
export class SearchThumbnailComponent implements OnInit {
	@Input() media;

	constructor() { }

	ngOnInit() {
	}

}
