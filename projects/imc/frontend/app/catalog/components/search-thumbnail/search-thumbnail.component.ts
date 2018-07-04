import { Component, Input, OnChanges } from '@angular/core';
import { MediaUtilsService } from '../../services/media-utils.service'

@Component({
	selector: 'search-thumbnail',
	templateUrl: './search-thumbnail.component.html',
	styleUrls: ['./search-thumbnail.component.css']
})
export class SearchThumbnailComponent implements OnChanges {
	@Input() media;
	identifyingTitle: string;
	description: string;

	constructor() { }

	ngOnChanges() {
		this.identifyingTitle = MediaUtilsService.getIdentifyingTitle(this.media);
		this.description = MediaUtilsService.getDescription(this.media);
	}
}
