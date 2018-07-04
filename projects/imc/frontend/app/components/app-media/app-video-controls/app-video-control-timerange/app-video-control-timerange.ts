import {Component, ViewChild, ElementRef} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-timerange',
    templateUrl: 'app-video-control-timerange.html'
})

export class AppVideoControlTimerangeComponent extends AppVideoControlComponent {

    @ViewChild('timeranges') timeranges: ElementRef;

    constructor() {
        super();
    }

    onprogress () {

        let frame = this.timeranges.nativeElement.clientWidth / this.video.duration;
        if (isNaN(frame)) return;

        while (this.timeranges.nativeElement.firstChild) {
            this.timeranges.nativeElement.removeChild(this.timeranges.nativeElement.firstChild);
        }

        for (let i = 0; i < this.video.buffered.length; i++) {

            let tr = document.createElement('div');

            let startX = this.video.buffered.start(i) * frame;
            let width = (this.video.buffered.end(i) * frame) - startX;

            tr.className = 'timerange';
            tr.style.left = `${startX}px`;
            tr.style.width = `${width}px`;

            this.timeranges.nativeElement.appendChild(tr);

        }
        
    }

}