import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { Observable } from 'rxjs/Observable';
import { catchError, map } from 'rxjs/operators';
import { MediaEntity, Providers } from './data'

export interface SearchFilter {
	searchTerm: string,
	itemType: string,
	terms: SearchTerm[],
	provider: string,
	country: string,
	productionYearFrom: number,
	productionYearTo: number,
	iprstatus: string
}

export interface SearchTerm {
	iri?: string,
	label: string
}

const matchFields = ["title", "contributor", "keyword"];

@Injectable()
export class CatalogService {
	private _data: MediaEntity[] = [];
	private _countByYears: any;
	private _countByProviders: any;

	constructor(private api: ApiService) { }

	/**
     * Search for media entities from the catalog.
     * @param filter
     * @param pageIdx
     * @param pageSize
     */
	search(filter: SearchFilter, pageIdx: number, pageSize: number) {
		let endpoint = 'search?currentpage=' + pageIdx + '&perpage=' + pageSize;
		let data = {
			match: null,
			filter: {
				type: filter.itemType,
				provider: filter.provider,
				iprstatus: filter.iprstatus,
				yearfrom: filter.productionYearFrom,
				yearto: filter.productionYearTo,
				terms: filter.terms
			}
		}
		if (filter.searchTerm) {
			data.match = { term: filter.searchTerm, fields: matchFields }
		}
		return this.api.post(endpoint, data, { "rawResponse": true });
	}

	/**
	 * Look for get-tags.
	 * @param pin
	 * @param distance
	 * @param cFilter
	 */
	getGeoDistanceAnnotations(pin, distance, filter) {
		let data = {
            filter: {
                type: "TAG",
                geo_distance: {
                    distance: distance,
                    location: {
                        lat: pin[0],
                        long: pin[1]
                    }
                },
                creation: null
            }
        };
        // setup filter for media entities
        if (filter !== undefined) {
        	let creation = {
				match: null,
				filter: {
					type: filter.itemType,
					provider: filter.provider,
					iprstatus: filter.iprstatus,
					yearfrom: filter.productionYearFrom,
					yearto: filter.productionYearTo
				}
			}
			if (filter.searchTerm) {
				creation.match = { term: filter.searchTerm, fields: matchFields }
			}
            data.filter.creation = creation;
        }
        return this.api.post('annotations/search', data, { "rawResponse": true });
	}

	/**
	 * Retrieve a list of relevant creations for given creation uuids and related place ids.
	 * @param relevantCreations
	 */
    getRelevantCreations = function(relevantCreations) {
        if (relevantCreations === undefined || relevantCreations.size === 0) {
        	return Observable.of({'Response': {'data': []}});
        }
        let data = {
            'relevant-list': []
        };
        for (let entry of Array.from(relevantCreations.entries())) {
		    let item = {
                'creation-id': entry[0],
                'place-ids': Array.from(entry[1])
            };
            data['relevant-list'].push(item);
		}
        return this.api.post('search_place', data, { "rawResponse": true });
    };

	getProviderPosition(provider: string) {
		for (let p of Providers) {
			if (p.code === provider) {
				return p.city.position;
			}
		}
	}

	getProviderCity(provider: string) {
		for (let p of Providers) {
			if (p.code === provider) {
				return p.city;
			}
		}
	}

}