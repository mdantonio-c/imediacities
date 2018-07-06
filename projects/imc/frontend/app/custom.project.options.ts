import { Injectable } from '@angular/core';
import { FormlyFieldConfig } from '@ngx-formly/core';

@Injectable()
export class ProjectOptions {

	constructor() {}

	public get_option(opt) {

		if (opt == 'registration') {
			return this.registration_options()
		}

		return null;
	}

	
	private registration_options() {

		let fields: FormlyFieldConfig[] = []; 

		fields.push(
            {
                "key": 'research_optin',
                "type": 'checkbox',
                "templateOptions": {
                    "label": 'Accept conditions... '
                },
                "validators": {
                    "fieldMatch": {
                        "expression": (control) => control.value,
                        "message": "You have to accept!"
                    }
                }
            }
        );

        let disclaimer = "Registration disclaimer<br><i>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</i>"
		return {"fields": fields, "disclaimer": disclaimer}
	}

}