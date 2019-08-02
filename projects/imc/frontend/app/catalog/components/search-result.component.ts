import { Component, Input, OnInit, OnChanges, Injector } from '@angular/core';
import { Router } from '@angular/router';
import { MediaUtilsService } from '../services/media-utils.service'
import { AuthService } from "/rapydo/src/app/services/auth";

@Component({
    selector: 'search-result',
    template: ''
})
export class SearchResultComponent implements OnInit, OnChanges {
	@Input() media;

	private authService: AuthService;

	identifyingTitle: string;
	description: string;
	private user: any;

	constructor(private authService: AuthService, private router: Router, private injector: Injector) {
		console.log("SearchResultComponent.constructor")
		console.log(authService);
		console.log(this.authService);
		console.log(this.injector);
		this.authService = this.injector.get(AuthService);
	}

	ngOnInit() {}
    ngAfterViewInit() {
		console.log("SearchResultComponent.ngAfterViewInit")
    	console.log(this.authService);
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

	disableSaveAs() { return false; }

	route(mediaId, mediaType) {
		if (mediaType === 'nonaventity') {
			this.router.navigate(['/app/catalog/images', mediaId]);
		} else {
			this.router.navigate(['/app/catalog/videos', mediaId]);
		}
	}

	protected getUser() {
		return this.user;
	}
}