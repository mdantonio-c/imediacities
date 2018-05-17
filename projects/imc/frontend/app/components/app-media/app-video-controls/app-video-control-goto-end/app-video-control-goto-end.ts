import {Component, Input, OnInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";
import {AppVideoRangePlayer} from "../../../../services/app-video-range-player";

@Component({
    selector: 'app-video-control-goto-end',
    templateUrl: 'app-video-control-goto-end.html'
})

export class AppVideoControlGotoEndComponent extends AppVideoControlComponent  {

    constructor(private RangePlayer: AppVideoRangePlayer) {
        super();
    }

    goto_end () {
        this.video.pause();
        this.video.currentTime = this.parent.player.begin + this.parent.player.duration;
    }
}