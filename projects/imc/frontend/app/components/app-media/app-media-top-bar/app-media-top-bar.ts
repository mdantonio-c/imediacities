import {Component, Input, OnInit} from '@angular/core';
import {Location} from '@angular/common';

@Component({
    selector: 'app-media-top-bar',
    templateUrl: 'app-media-top-bar.html'
})

export class AppMediaTopBarComponent implements OnInit {

    @Input() type_media;

    constructor(private _location: Location) {
    }

    backClicked() {
        this._location.back();
    }

    ngOnInit() {
    }
}