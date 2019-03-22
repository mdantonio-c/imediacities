import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { Router } from '@angular/router';
import { ListsService } from '../../../services/lists.service'

export interface ItemDetail {
	id: string,
	title: string,
	type?: string,
	description?: string,
	thumbnail?: string,
	focus?: boolean
}

@Component({
	selector: 'item-detail',
	templateUrl: './item-detail.component.html',
	styleUrls: ['./item-detail.component.css'],
	/*changeDetection: ChangeDetectionStrategy.OnPush*/
})
export class ItemDetailComponent {

	@Input() media: ItemDetail;
	@Input() focus: boolean;
	@Output() onDelete: EventEmitter<null> = new EventEmitter<null>();
	selected = false;

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

	select() {
		/*this.selected = true;*/
    	this.listsService.selectList(this.media);
	}

}