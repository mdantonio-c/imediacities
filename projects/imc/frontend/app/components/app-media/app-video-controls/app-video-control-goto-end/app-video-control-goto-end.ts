import {Component, Input, OnInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-goto-end',
    templateUrl: 'app-video-control-goto-end.html'
})

export class AppVideoControlGotoEndComponent extends AppVideoControlComponent  {

    constructor() {
        super();
    }

    goto_end () {
        this.video.pause();
        this.video.currentTime = this.video.duration;
    }
}