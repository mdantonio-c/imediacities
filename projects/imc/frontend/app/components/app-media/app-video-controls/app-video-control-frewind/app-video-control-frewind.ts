import {Component, OnInit} from '@angular/core';
import {AppVideoControlFastPlayComponent} from "../app-video-control-fast-play";

@Component({
    selector: 'app-video-control-frewind',
    templateUrl: 'app-video-control-frewind.html'
})

export class AppVideoControlFrewindComponent extends AppVideoControlFastPlayComponent {

    constructor() {
        super()
    }

    frewind () {
        this.fast_play(-1);
    }


}