import { Injectable } from '@angular/core';

@Injectable()
export class MediaUtilsService {

	static getIdentifyingTitle(media: any): string {
		let identifyingTitle: string;
		let entityType: string = media.type;
		if (entityType === 'aventity') {
			// aventity: metadata comes with identitying_title
			identifyingTitle = media.attributes.identifying_title;
		} else {
			// nonaventity: first choice in english
			for (let t of media.relationships.titles) {
				if (t.attributes.hasOwnProperty('language') && t.attributes.language && t.attributes.language.key === 'en') {
					identifyingTitle = t.attributes.text;
					break;
				}
			}
			// otherwise take the first on the list 
			if (!identifyingTitle) {
				identifyingTitle = media.relationships.titles[0].attributes.text;
			}
		}
		return identifyingTitle;
	}

	static getDescription(media: any, lang: string = 'en'): string {
		let description: string;
		let first: boolean = true;
		for (let d of media.relationships.descriptions) {
			// take the first as default
			if (first) {
				first = !first;
				description = d.attributes.text;
			}
			if (d.attributes.hasOwnProperty('language') && d.attributes.language && d.attributes.language.key === lang) {
				description = d.attributes.text;
				break;
			}
		}
		return description;
	}
}