import {Component, Input, OnInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-goto-start',
    templateUrl: 'app-video-control-goto-start.html'
})

export class AppVideoControlGotoStartComponent extends AppVideoControlComponent {

    constructor() {
        super();
    }

    goto_start () {
        this.video.pause();
        this.video.currentTime = this.parent.player.begin;
    }
}