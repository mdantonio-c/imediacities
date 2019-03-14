import { Component, Input, OnInit, OnChanges } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Location } from '@angular/common';
import { AuthService } from "/rapydo/src/app/services/auth";
import { NotificationService } from '/rapydo/src/app/services/notification';
import { ListsService } from '../../../services/lists.service';
import { UserList } from '../../../services/lists.model';

@Component({
    selector: 'app-media-top-bar',
    templateUrl: 'app-media-top-bar.html',
    styleUrls: ['./app-media-top-bar.css']
})
export class AppMediaTopBarComponent implements OnInit, OnChanges {

    @Input() item_type: string;
    @Input() item_id: string;
    icon = '';
    label = '';

    user: any;
    my_lists: UserList[] = [];
    listCreation: boolean = false;
    listForm: FormGroup;

    constructor(
        private _location: Location,
        private authService: AuthService,
        private listsService: ListsService,
        private formBuilder: FormBuilder,
        private notify: NotificationService) {
        this.listForm = this.formBuilder.group({
            name: ['', Validators.required],
            description: ['', Validators.required]
        });
    }

    backClicked() {
        this._location.back();
    }

    media_type_set() {
        if (this.item_type === 'video') {
            this.icon = 'videocam';
            this.label = 'VIDEO';
        } else if (this.item_type === 'image') {
            this.icon = 'image';
            this.label = 'PHOTO';
        }
    }

    ngOnInit() {
        this.user = this.authService.getUser();
    }

    ngOnChanges() {
        this.media_type_set();
    }

    openAddListPanel(event) {
        if (event) {
            this.listCreation = false;
            this.resetForm();
            // load my lists
            this.loadMyLists();
        }
    }

    private loadMyLists() {
        this.listsService.getLists().subscribe(resp => {
            this.my_lists = this.listsService.parseLists(resp.data);
        }, error => {
            console.error(`There was an error loading lists: $()`);
            this.notify.showError('Error in loading lists');
        });
    }

    addToList(event, listId) {
        event.preventDefault();
        let target = 'item:' + this.item_id;
        console.log('add this <' + target + '> to the list <' + listId + '>');
        this.listsService.addItemToList(target, listId).subscribe(resp => {
            // item added to the list
            // 
        }, error => {
            console.error(`There was an error adding item to the list: $(error.erros)`);
            this.notify.showError('Error in adding this item to the list');
        });
    }

    listCreationToggle() {
        this.listCreation = !this.listCreation;
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
            this.notify.extractErrors(error, this.notify.ERROR);
        });
    }

    private resetForm() {
        this.listForm.reset({ 'name': '', 'description': '' });
    }
}