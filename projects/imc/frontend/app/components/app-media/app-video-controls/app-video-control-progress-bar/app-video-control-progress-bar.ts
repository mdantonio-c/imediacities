import {Component, ViewChild, ElementRef, Input} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-progress-bar',
    templateUrl: 'app-video-control-progress-bar.html'
})

export class AppVideoControlProgressBarComponent extends AppVideoControlComponent {

    @ViewChild('progress') progress: ElementRef;

    constructor() {
        super();
    }

    update (e) {
        this.progress.nativeElement.value = (e.offsetX - this.progress.nativeElement.offsetLeft) / this.progress.nativeElement.offsetWidth;
        this.video.currentTime = this.parent.player.begin + this.progress.nativeElement.value * this.parent.player.duration;
    }

    ontimeupdate () {
        this._progress_set(Math.abs(this.video.currentTime - this.parent.player.begin) / this.parent.player.duration);
    }

    onbegin () {
        this._progress_set(0);
    }

    onended () {
        this._progress_set(1);
    }

    _progress_set (value) {
        this.progress.nativeElement.value = value
    }

}