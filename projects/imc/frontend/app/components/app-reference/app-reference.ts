import { Component, Input, OnInit } from '@angular/core';
import { AppAnnotationsService } from "../../services/app-annotations";
import { IMC_Annotation } from "../../services/app-shots";

@Component({
	selector: 'app-reference',
	templateUrl: 'app-reference.html'
})

export class AppReferenceComponent implements OnInit {

	@Input("reference") biblio: IMC_Annotation;
	@Input() can_delete = false;

	constructor(
		private AnnotationsService: AppAnnotationsService
	) {
	}

	delete() {
		if (!this.can_delete) return;
		if (this.biblio.id) {
			this.AnnotationsService.delete_tag(this.biblio, this.biblio.source);
		}
	}

	ngOnInit() { }
}