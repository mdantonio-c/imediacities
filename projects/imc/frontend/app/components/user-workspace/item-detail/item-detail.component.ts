import { Component, Input, Output, EventEmitter} from '@angular/core';
import { Router } from '@angular/router';
import { ListsService } from '../../../services/lists.service'

export interface ItemDetail {
	id: string,
	title: string,
	type?: string,
	description?: string,
	thumbnail?: string,
	focus?: boolean,
	listItem?: boolean,
	listId?: string
}

@Component({
	selector: 'item-detail',
	templateUrl: './item-detail.component.html',
	styleUrls: ['./item-detail.component.css'],
})
export class ItemDetailComponent {

	@Input() media: ItemDetail;
	@Output() onDelete: EventEmitter<null> = new EventEmitter<null>();

	constructor(
		private router: Router,
		private listsService: ListsService) { }

	disableSaveAs() { return false; }

	route(mediaId, mediaType) {
		if (mediaType === 'nonaventity') {
			this.router.navigate(['/app/catalog/images', mediaId]);
		} else if (mediaType === 'aventity') {
			this.router.navigate(['/app/catalog/videos', mediaId]);
		}
	}

	delete() {
		this.onDelete.emit();
	}

	loadListItems() {
    	this.listsService.selectList(this.media);
	}

}