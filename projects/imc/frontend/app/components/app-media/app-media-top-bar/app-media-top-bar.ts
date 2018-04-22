import {Component, OnInit} from '@angular/core';

@Component({
    selector: 'app-media-top-bar',
    templateUrl: 'app-media-top-bar.html'
})

export class AppMediaTopBarComponent implements OnInit {
    /* esempio del cambiamento per il tipo di media, test topbar*/
    public mediaType: string;

    constructor() {
        this.mediaType = 'video';
    }

    ngOnInit() {
    }
}