import {Component, OnInit} from '@angular/core';
import {Location} from '@angular/common';

@Component({
    selector: 'app-media-top-bar',
    templateUrl: 'app-media-top-bar.html'
})

export class AppMediaTopBarComponent implements OnInit {
    /* esempio del cambiamento per il tipo di media, test topbar*/
    public mediaType: string;

    constructor(private _location: Location) {
        this.mediaType = 'video';
    }

    backClicked() {
        this._location.back();
    }

    ngOnInit() {
    }
}