import { Component, OnInit, Input } from '@angular/core';
import { Router } from '@angular/router';

export interface ItemDetail {
	id: string,
	title: string,
	type?: string,
	description?: string,
	thumbnail?: string
}

@Component({
	selector: 'item-detail',
	templateUrl: './item-detail.component.html',
	styleUrls: ['./item-detail.component.css'],
})
export class ItemDetailComponent implements OnInit {

	@Input() media: ItemDetail;

	constructor(private router: Router) { }

	disableSaveAs() { return false; }

	route(mediaId, mediaType) {
		if (mediaType === 'nonaventity') {
			this.router.navigate(['/app/catalog/images', mediaId]);
		} else if (mediaType === 'aventity') {
			this.router.navigate(['/app/catalog/videos', mediaId]);
		}
	}

	ngOnInit() {

	}

	removeList() {
		console.log('remove list', this.media.title);
	}

}