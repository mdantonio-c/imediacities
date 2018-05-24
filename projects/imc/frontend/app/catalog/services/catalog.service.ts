import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { MediaEntity } from './data'

export interface SearchFilter {
	searchTerm: string,
	itemType: string,
	terms: string[],
	city: string,
	productionYear: string,
	iprstatus: string
}

const matchFields =  ["title", "contributor", "keyword"];

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
	search(filter, pageIdx, pageSize) {
		let endpoint = 'search?currentpage=' + pageIdx + '&perpage=' + pageSize;
		let data = {
			match: null,
			filter: {
				type: filter.itemType,
				provider: filter.city,
				iprstatus: filter.iprstatus
			}
		}
		if (filter.searchTerm) {
			data.match = { term: filter.searchTerm, fields: matchFields}
		}
		return this.api.post(endpoint, data);
	}

	/*get countByYears() {
		return this._countByYears;
	}

	get countByProviders() {
		return this._countByProviders;
	}

	mediaEntity(uuid: string) {
		return this._data.find(row => {
			return row.id === uuid;
		});
	}*/

}