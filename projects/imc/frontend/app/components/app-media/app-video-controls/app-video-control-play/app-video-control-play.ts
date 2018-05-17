import {Component} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-play',
    templateUrl: 'app-video-control-play.html'
})

export class AppVideoControlPlayComponent extends AppVideoControlComponent {

    constructor() {
        super();
    }

    play () {

        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }

    }
}