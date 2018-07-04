import {Component, Input, OnInit, OnChanges} from '@angular/core';
import {Location} from '@angular/common';

@Component({
    selector: 'app-media-top-bar',
    templateUrl: 'app-media-top-bar.html'
})

export class AppMediaTopBarComponent implements OnInit, OnChanges {

    @Input() media_type;
    public icon = '';
    public label = '';

    constructor(private _location: Location) {
    }

    backClicked() {
        this._location.back();
    }

    media_type_set () {
        if (this.media_type === 'video') {
            this.icon = 'videocam';
            this.label = 'VIDEO';
        } else if (this.media_type === 'image') {
            this.icon = 'image';
            this.label = 'PHOTO';
        }
    }

    ngOnInit() {}

    ngOnChanges () {
        this.media_type_set();
    }
}