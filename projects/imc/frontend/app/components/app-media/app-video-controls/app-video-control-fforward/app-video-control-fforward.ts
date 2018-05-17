import {Component, OnInit} from '@angular/core';

import {AppVideoControlFastPlayComponent} from "../app-video-control-fast-play";

@Component({
    selector: 'app-video-control-fforward',
    templateUrl: 'app-video-control-fforward.html'
})

export class AppVideoControlFforwardComponent extends AppVideoControlFastPlayComponent {

    constructor() {
        super()
    }

    fforward () {
        this.fast_play(1);
    }


}