import { Component, Input } from '@angular/core';

@Component({
	selector: 'search-media-tag',
	templateUrl: './search-media-tag.component.html',
	styleUrls: ['./search-media-tag.component.css']
})
export class SearchMediaTagComponent {
	@Input() media;
}