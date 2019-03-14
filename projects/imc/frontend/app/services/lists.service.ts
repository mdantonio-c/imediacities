import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { UserList } from './lists.model';

@Injectable()
export class ListsService {

	constructor(private api: ApiService) { }

	getLists() {
		return this.api.get('lists');
	}

	parseLists(lists: any[]) : UserList[] {
		let parsed_lists: UserList[] = [];
		lists.forEach((lst, index) => {
			parsed_lists.push({
				"uuid": lst.id,
				"name": lst.attributes.name,
				"description": lst.attributes.description
			});
		});
		return parsed_lists.sort((a, b) => a.name.localeCompare(b.name));
	}

	addItemToList(target: string, listId: string) {
		return this.api.post(`lists/${listId}/items`, {
			'target': `${target}`
		});
	}

	create(list: UserList) {
		return this.api.post('lists', list);
	}
}