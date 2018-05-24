import { Component, Input, OnInit } from '@angular/core';

@Component({
	selector: 'search-media',
	templateUrl: './search-media.component.html',
	styleUrls: ['./search-media.component.css']
})
export class SearchMediaComponent implements OnInit {
	@Input() media;

	constructor() { }

	ngOnInit() {
	}

}