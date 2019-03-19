import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { UserList } from './lists.model';

@Injectable()
export class ListsService {

	constructor(private api: ApiService) { }

	getLists(itemId?: string) {
		let params = itemId ? {'item':itemId} : {};
		return this.api.get('lists', '', params);
	}

	parseLists(lists: any[]) : UserList[] {
		let parsed_lists: UserList[] = [];
		lists.forEach((lst, index) => {
			let item: UserList = {
				"uuid": lst.id,
				"name": lst.attributes.name,
				"description": lst.attributes.description,
				"belong": lst.belong ? true : false
			};
			/*if (lst.belong) { item['belong'] = true }*/
			parsed_lists.push(item);
		});
		return parsed_lists.sort((a, b) => a.name.localeCompare(b.name));
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
}