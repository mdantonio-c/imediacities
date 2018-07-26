import { Injectable } from '@angular/core';
import { FormlyFieldConfig } from '@ngx-formly/core';

@Injectable()
export class ProjectOptions {

	constructor() {}

	public get_option(opt) {

		if (opt == 'registration') {
			return this.registration_options()
		}

        if (opt == 'user_page') {
            return {
                "group": true,
                "custom": [
                    {name: 'Institution', prop: "declared_institution", flexGrox: 1.0}
                ]
            }
        }

		return null;
	}

	
	private registration_options() {

		let fields: FormlyFieldConfig[] = []; 

		fields.push(
            {
                "key": 'declared_institution',
                "type": 'select',
                "templateOptions": {
                    "label": 'Do you work at one of the following institutions:',
                    "required": true,
                    "addonLeft": {
                        "class": "fa fa-bank"
                    },
                    "options": [
                      { label: 'Archive', value: 'archive' },
                      { label: 'University', value: 'university' },
                      { label: 'Research Institution', value: 'research_institution' },
                      { label: 'None of the above', value: 'none' },
                    ]
                }
            },
            {
                "className": "section-label",
                "template": "<hr><div><strong>To protect your privacy we ask you to accept our:</strong></div><br>"
            },
            {
                "key": 'terms_of_use_optin',
                "type": 'terms_of_use',
                "templateOptions": {
                    "label": 'Terms of Use',
                    "terms_of_use": require("./terms_of_use.html") 
                },
                "validators": {
                    "fieldMatch": {
                        "expression": (control) => control.value,
                    }
                }
            },
            {
                "key": 'privacy_policy_optin',
                "type": 'terms_of_use',
                "templateOptions": {
                    "label": 'Privacy Policy',
                    "terms_of_use": require("./privacy_policy.html") 
                },
                "validators": {
                    "fieldMatch": {
                        "expression": (control) => control.value,
                    }
                }
            },
            {
                "key": 'research_optin',
                "type": 'terms_of_use',
                "templateOptions": {
                    "label": 'Research declaration',
                    "terms_of_use": require("./research_declaration.html")
                },
                "validators": {
                    "fieldMatch": {
                        "expression": (control) => control.value,
                    }
                }
            }

        );

        let disclaimer = `
Welcome to the registration page of I-Media-Cities. Registering a personal account is free of charge, in compliance with European law, and will allow you to enjoy a whole list of additional platform functionalities, such as adding your own information to films and photographs.<br>
<br>
It's quick and simple – register now and join a large community all over Europe. 
`;
		return {"fields": fields, "disclaimer": disclaimer}
	}

}