import {Component, OnInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";
import {AppVideoControlsFastPlayService} from "../../../../services/app-video-controls-fast-play";

@Component({
    selector: 'app-video-control-frewind',
    templateUrl: 'app-video-control-frewind.html'
})

export class AppVideoControlFrewindComponent extends AppVideoControlComponent {

    stato = 0;

    constructor(private AppVideoControlsFastPlay: AppVideoControlsFastPlayService) {
        super()
    }

    frewind () {
        this.AppVideoControlsFastPlay.fast_play(-1, this.video);
    }

    onplay () {
        this.parent.spinner_prevent = false;
        this.AppVideoControlsFastPlay.stop();
    }

    onbegin () {
        this.parent.spinner_prevent = false;
        this.AppVideoControlsFastPlay.stop();
    }

    onended () {
        this.parent.spinner_prevent = false;
        this.AppVideoControlsFastPlay.stop();
    }

    onseeked () {
        this.parent.spinner_prevent = this.AppVideoControlsFastPlay.interval !== null;
    }

    onseeking () {
        this.parent.spinner_prevent = this.AppVideoControlsFastPlay.interval !== null;
    }

}