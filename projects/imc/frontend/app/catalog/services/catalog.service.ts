import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { Observable } from 'rxjs/Observable';
import { catchError, map } from 'rxjs/operators';
import { MediaEntity } from './data'

export interface SearchFilter {
	searchTerm: string,
	itemType: string,
	terms: string[],
	provider: string,
	country: string,
	productionYearFrom: number,
	productionYearTo: number,
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
	search(filter: SearchFilter, pageIdx: number, pageSize: number) {
		let endpoint = 'search?currentpage=' + pageIdx + '&perpage=' + pageSize;
		let data = {
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
			data.match = { term: filter.searchTerm, fields: matchFields}
		}
		/*this.api.post(endpoint, data, {"rawResponse": true}).pipe(
			map(response => {}),
			catchError((error, caught) => {})
		);*/
		return this.api.post(endpoint, data, {"rawResponse": true});
		/*return this.api.post(endpoint, data);*/
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