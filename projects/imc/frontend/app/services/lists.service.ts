import { Injectable } from '@angular/core';
import { ApiService } from '@rapydo/services/api';
import { UserList } from './lists.model';
import { Subject }    from 'rxjs';

@Injectable()
export class ListsService {

	private listSelectedSource = new Subject<any>();
	listSelected$ = this.listSelectedSource.asObservable();

	constructor(private api: ApiService) { }

	getLists(itemId?: string, includeNumberOfItems?: boolean) {
		let params = itemId ? {'item':itemId} : {};
		if (includeNumberOfItems) {
			params['includeNumberOfItems'] = true;
		}
		return this.api.get('lists', '', params);
	}

	parseLists(lists: any[]) : UserList[] {
		let parsed_lists: UserList[] = [];
		lists.forEach((lst, index) => {
			let item: UserList = {
				"uuid": lst.id,
				"name": lst.name,
				"description": lst.description,
				"belong": lst.belong ? true : false
			};
			/*if (lst.belong) { item['belong'] = true }*/
			parsed_lists.push(item);
		});
		return parsed_lists.sort((a, b) => a.name.localeCompare(b.name));
	}

	updateList(listId: string, data: any) {
		return this.api.put('lists', listId, data);
	}

	removeList(listId: string) {
		return this.api.delete('lists', listId);
	}

	getListItems(listId: string) {
		return this.api.get(`lists/${listId}/items`);
	}

	addItemToList(target: string, listId: string) {
		return this.api.post(`lists/${listId}/items`, {
			'target': `${target}`
		});
	}

	removeItemfromList(itemId: string, listId: string) {
		return this.api.delete(`lists/${listId}/items`, itemId);
	}

	create(list: UserList) {
		return this.api.post('lists', list);
	}

	selectList(list) {
		this.listSelectedSource.next(list);
	}
}