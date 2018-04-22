import {Component, ViewChild, ElementRef, Input, AfterViewInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-progress-bar',
    templateUrl: 'app-video-control-progress-bar.html'
})

export class AppVideoControlProgressBarComponent extends AppVideoControlComponent implements AfterViewInit {

    @ViewChild('progress') progress: ElementRef;

    constructor() {
        super();
    }

    update (e) {
        this.progress.nativeElement.value = (e.offsetX - this.progress.nativeElement.offsetLeft) / this.progress.nativeElement.offsetWidth;
        this.video.currentTime = this.progress.nativeElement.value * this.video.duration;
    }

    ontimeupdate () {
        this.progress.nativeElement.value = this.video.currentTime / this.video.duration;
    }

    ngAfterViewInit () {
        //console.log("progress.nativeElement",  this.progress.nativeElement);
    }
}