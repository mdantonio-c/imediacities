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
	listId?: string,
	ref?: any
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

	route() {
		if (this.media.listItem) {
			// here media.id is item UUID
			// list item conveys with creation model in ref
			let media = this.media.ref;
			if (media.type === 'shot' || media.attributes.item_type['key'] === 'Video') {
				this.router.navigate(['/app/catalog/videos',  media.creation_id]);
			} else {
				this.router.navigate(['/app/catalog/images', media.creation_id]);
			}
		} else {
			// here media.id is aventity/nonaventity UUID
			switch (this.media.type) {
				case "nonaventity":
					this.router.navigate(['/app/catalog/images', this.media.id]);
					break;
				case "aventity":
					this.router.navigate(['/app/catalog/videos', this.media.id]);
					break;
			}
		}
	}

	delete() {
		this.onDelete.emit();
	}

	loadListItems() {
    	this.listsService.selectList(this.media);
	}

}