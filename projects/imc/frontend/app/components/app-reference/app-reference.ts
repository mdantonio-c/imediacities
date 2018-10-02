import { Component, Input, OnInit } from '@angular/core';
import { AppAnnotationsService } from "../../services/app-annotations";
import { IMC_Annotation } from "../../services/app-shots";
import * as moment from 'moment';

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
			this.AnnotationsService.delete_anno(this.biblio, this.biblio.source);
		}
	}

	printMonth(monthNum) {
		return moment.monthsShort(monthNum - 1);
	}

	ngOnInit() { }
}