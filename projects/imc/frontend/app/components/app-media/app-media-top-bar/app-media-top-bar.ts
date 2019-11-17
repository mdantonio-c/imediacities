import { Component, Input, OnInit, OnChanges } from '@angular/core';
import { Location } from '@angular/common';
import { AuthService } from "@rapydo/services/auth";

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

    constructor(
        private _location: Location,
        private authService: AuthService) { }

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
}