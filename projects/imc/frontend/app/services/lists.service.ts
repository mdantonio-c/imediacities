import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";
import { UserList } from "./lists.model";
import { Subject, Observable } from "rxjs";
import { UserListEntity } from "@app/types";

@Injectable({
  providedIn: "root",
})
export class ListsService {
  private listSelectedSource = new Subject<any>();
  listSelected$ = this.listSelectedSource.asObservable();

  constructor(private api: ApiService) {}

  getLists(
    itemId?: string,
    includeNumberOfItems?: boolean
  ): Observable<UserListEntity[]> {
    let params = itemId ? { item: itemId } : {};
    if (includeNumberOfItems) {
      params["includeNumberOfItems"] = true;
    }
    return this.api.get("lists", params);
  }

  parseLists(lists: any[]): UserList[] {
    let parsed_lists: UserList[] = [];
    lists.forEach((lst, index) => {
      let item: UserList = {
        uuid: lst.id,
        name: lst.name,
        description: lst.description,
        belong: lst.belong ? true : false,
      };
      /*if (lst.belong) { item['belong'] = true }*/
      parsed_lists.push(item);
    });
    return parsed_lists.sort((a, b) => a.name.localeCompare(b.name));
  }

  updateList(listId: string, data: any) {
    return this.api.put("lists", listId, data);
  }

  removeList(listId: string) {
    return this.api.delete("lists", listId);
  }

  getListItems(listId: string): Observable<any[]> {
    return this.api.get(`lists/${listId}/items`);
  }

  addItemToList(item_type: string, item_id: string, listId: string) {
    return this.api.post(`lists/${listId}/items`, {
      target: {
        type: item_type,
        id: item_id,
      },
    });
  }

  removeItemfromList(itemId: string, listId: string) {
    return this.api.delete(`lists/${listId}/items`, itemId);
  }

  create(list: UserList) {
    return this.api.post("lists", list);
  }

  selectList(list) {
    this.listSelectedSource.next(list);
  }
}
