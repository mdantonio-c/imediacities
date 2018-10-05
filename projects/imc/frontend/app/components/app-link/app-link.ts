import { Component, Input } from '@angular/core';
import { AppAnnotationsService } from "../../services/app-annotations";
import { IMC_Annotation } from "../../services/app-shots";

@Component({
	selector: 'app-link',
	templateUrl: 'app-link.html'
})

export class AppLinkComponent {

	@Input() link: IMC_Annotation;
	@Input() can_delete = false;

	constructor(private AnnotationsService: AppAnnotationsService) { }

	delete() {
		if (!this.can_delete) return;
		if (this.link.id) {
			this.AnnotationsService.delete_anno(this.link, this.link.source);
		}
	}
}