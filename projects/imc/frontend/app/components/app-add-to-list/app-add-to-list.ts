import { Component, Input } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NotificationService } from '@rapydo/services/notification';
import { ListsService } from '../../services/lists.service';
import { UserList } from '../../services/lists.model';

@Component({
	selector: 'app-add-to-list',
	templateUrl: './app-add-to-list.html',
	styleUrls: ['./app-add-to-list.css']
})
export class AppAddToListComponent {

	@Input() item_id: string;
    @Input() item_type: string = 'item';    // 'item' or 'shot'
    @Input() flag: string;

	my_lists: UserList[] = [];
    listCreation: boolean = false;
    listForm: FormGroup;

	constructor(
		private listsService: ListsService,
        private formBuilder: FormBuilder,
        private notify: NotificationService) {
		this.listForm = this.formBuilder.group({
            name: ['', Validators.required],
            description: ['', Validators.required]
        });
	}

	openAddListPanel(event) {
        if (event) {
            this.listCreation = false;
            this.resetForm();
            // load my lists
            this.loadMyLists();
        }
    }

    listCreationToggle() {
        this.listCreation = !this.listCreation;
    }

    toggleItem(event, listId, isMember) {
        event.preventDefault();
        isMember ? this.removeFromList(listId) : this.addToList(listId);
    }

    createList() {
        console.log('create list', this.listForm.value);
        this.listsService.create(this.listForm.value).subscribe(response => {
            console.log('list created successfully', response);
            this.listCreation = false;
            // refresh my lists
            this.loadMyLists();
        }, error => {
            console.error('There was an error creating list', error.errors);
            this.notify.showError(error);
        });
    }

    private loadMyLists() {
        this.listsService.getLists(this.item_id).subscribe(resp => {
            this.my_lists = this.listsService.parseLists(resp.data);
            /*console.log(this.my_lists);*/
        }, error => {
            console.error('There was an error loading lists', error.errors);
            this.notify.showError('Error in loading lists');
        });
    }

    private removeFromList(listId) {
        console.log(`remove <${this.item_type}:${this.item_id}> to the list <${listId}>`);
        this.listsService.removeItemfromList(this.item_id, listId).subscribe(resp => {
            // item removed from the list
            this.my_lists.filter(l => l.uuid == listId)[0].belong = false;
        }, error => {
            console.error('There was an error removing item from the list', error.errors);
            this.notify.showError('Error in removing this item from the list');
        });
    }

    private addToList(listId) {
        let target = `${this.item_type}:${this.item_id}`;
        console.log(`add this <${target}> to the list <${listId}>`);
        this.listsService.addItemToList(target, listId).subscribe(resp => {
            // item added to the list
            this.my_lists.filter(l => l.uuid == listId)[0].belong = true; 
        }, error => {
            console.error('There was an error adding item to the list', error.errors);
            this.notify.showError('Error in adding this item to the list');
        });
    }

    private resetForm() {
        this.listForm.reset({ 'name': '', 'description': '' });
    }
}