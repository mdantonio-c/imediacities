import { Component, Input, OnChanges } from '@angular/core';
import { MediaUtilsService } from '../../services/media-utils.service'

@Component({
	selector: 'search-media',
	templateUrl: './search-media.component.html',
	styleUrls: ['./search-media.component.css']
})
export class SearchMediaComponent implements OnChanges {
	@Input() media;
	identifyingTitle: string;
	description: string;

	constructor() { }

	ngOnChanges() {
		this.identifyingTitle = MediaUtilsService.getIdentifyingTitle(this.media);
		this.description = MediaUtilsService.getDescription(this.media);
	}

}