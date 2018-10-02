import { Component, Input, Output, EventEmitter } from '@angular/core';
import { AppAnnotationsService } from "../../../../services/app-annotations";
import { BibliographicReference } from "../../../../services/app-shots";
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { infoResult } from "../../../../decorators/app-info";
import { IsbnValidator } from "../../../../validators/isbn.validator";
import { DoiValidator } from "../../../../validators/doi.validator";
import { UrlValidator } from "../../../../validators/url.validator";

@Component({
	selector: 'app-modal-insert-reference',
	templateUrl: 'app-modal-insert-reference.html'
})
export class AppModalInsertReferenceComponent {

	@Input() data;
	@Input() media_type: string;

	@Output() shots_update: EventEmitter<any> = new EventEmitter();
	@infoResult() save_result;

	referenceForm: FormGroup;

	constructor(
		private AnnotationsService: AppAnnotationsService,
		private formBuilder: FormBuilder) {
		this.referenceForm = this.formBuilder.group({
			title: ['', Validators.required],
			authors: ['', Validators.required],
			book_title: [''],
			journal: [''],
			volume: [''],
			number: [''],
			year: [null],
			month: [null],
			editor: [''],
			publisher: [''],
			address: [''],
			url: ['', {validators: UrlValidator, updateOn: 'blur'}],
			isbn: ['', {validators: IsbnValidator, updateOn: 'blur'}],
			issn: [''],
			doi: ['', {validators: DoiValidator, updateOn: 'blur'}]
		});
	}

	save() {
		let form = this.referenceForm.value;
		let reference: BibliographicReference = {
			title: form.title.trim(),
		    authors: form.authors.split(",").map(item => item.trim())
		}
		if (form.book_title &&  form.book_title.trim() !== '') { reference.book_title = form.book_title.trim(); }
		if (form.journal &&  form.journal.trim() !== '') { reference.journal = form.journal.trim(); }
		if (form.volume &&  form.volume.trim() !== '') { reference.volume = form.volume.trim(); }
		if (form.number &&  form.number.trim() !== '') { reference.number = form.number.trim(); }
		if (form.year) { reference.year = form.year; }
		if (form.month) { reference.month = form.month; }
		if (form.editor &&  form.editor.trim() !== '') { reference.editor = form.editor.trim(); }
		if (form.publisher &&  form.publisher.trim() !== '') { reference.publisher = form.publisher.trim(); }
		if (form.address &&  form.address.trim() !== '') { reference.address = form.address.trim(); }
		if (form.url &&  form.url.trim() !== '') { reference.url = form.url.trim(); }
		if (form.isbn &&  form.isbn.trim() !== '') { reference.isbn = form.isbn.trim(); }
		if (form.doi &&  form.doi.trim() !== '') { reference.doi = form.doi.trim(); }
		/*console.log('save reference', reference);*/
		this.AnnotationsService.create_reference(
			this.data.shots.map(s => s.id),
			reference,
			this.media_type,
			(err, r) => {

				if (err) {
					this.save_result.show('error');
				}

				this.save_result.show('success', 'Reference added successfully');
				this.shots_update.emit(r);

				// reset form
				this.referenceForm.reset();
			}
		);
	}

	months = [
        {key: 'January', 	value: 1},
        {key: 'February', 	value: 2},
        {key: 'March', 		value: 3},
        {key: 'April',		value: 4},
        {key: 'May', 		value: 5},
        {key: 'June', 		value: 6},
        {key: 'July', 		value: 7},
        {key: 'August', 	value: 8},
        {key: 'September', 	value: 9},
        {key: 'October', 	value: 10},
        {key: 'November', 	value: 11},
        {key: 'December', 	value: 12},
    ];
}