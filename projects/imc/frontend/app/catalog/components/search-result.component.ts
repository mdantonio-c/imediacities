import { Component, Input, OnInit, OnChanges } from '@angular/core';
import { MediaUtilsService } from '../services/media-utils.service'
import { AuthService } from "/rapydo/src/app/services/auth";

@Component({
    selector: 'search-result',
    template: ''
})
export class SearchResultComponent implements OnInit, OnChanges {
	@Input() media;

	identifyingTitle: string;
	description: string;
	private user: any;

	constructor(private authService: AuthService) { }

	ngOnInit() {
		this.user = this.authService.getUser();
	}

	ngOnChanges() {
		this.identifyingTitle = MediaUtilsService.getIdentifyingTitle(this.media);
		this.description = MediaUtilsService.getDescription(this.media);
	}

	canRevise() {
		return this.user.roles.hasOwnProperty('Reviser') &&
			this.underRevision() &&
			this.user.uuid === this.media.relationships.item[0].relationships.revision[0].id;
	}

	underRevision() {
		return (this.media.relationships.item[0].relationships.revision) ? true : false;
	}

	protected getUser() {
		return this.user;
	}
}