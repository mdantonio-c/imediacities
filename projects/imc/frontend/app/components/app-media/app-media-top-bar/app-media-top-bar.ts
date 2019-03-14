import { Component, Input, OnInit, OnChanges } from '@angular/core';
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

    constructor(
        private _location: Location,
        private authService: AuthService,
        private listsService: ListsService,
        private notify: NotificationService) {
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

    loadMyLists(event) {
        if (event) {
            // load my lists
            this.listsService.getLists().subscribe(resp => {
                this.my_lists = this.listsService.parseLists(resp.data);
            }, error => {
                console.error(`There was an error loading lists: $()`);
                this.notify.showError('Error in loading lists');
            });
        }
    }

    addToList(event, listId) {
        event.preventDefault();
        let target = 'item:' + this.item_id;
        console.log('add this <'+target+'> to the list <'+listId+'>');
        this.listsService.addItemToList(target, listId).subscribe(resp => {
            // item added to the list
            // 
        }, error => {
            console.error(`There was an error addind item to the list: $()`);
            this.notify.showError('Error in adding this item to the list');
        });
    }
}