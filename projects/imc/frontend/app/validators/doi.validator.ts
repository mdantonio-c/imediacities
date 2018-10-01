import { AbstractControl, ValidatorFn } from '@angular/forms';

const doi_pattern = /^10\.\d{4,9}\/[-\.\_;\(\)\/:A-Z0-9]+$/i;

export function DoiValidator(control: AbstractControl): { [key: string]: any } {
	if (!control.value) {
		return null;
	}
	return doi_pattern.test(control.value) ? null : { doi: true };
}