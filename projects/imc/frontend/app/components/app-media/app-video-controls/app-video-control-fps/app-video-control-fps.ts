import {Component, OnInit, ViewChild, ElementRef, AfterViewInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-fps',
    templateUrl: 'app-video-control-fps.html'
})

export class AppVideoControlFpsComponent extends AppVideoControlComponent implements AfterViewInit {

    @ViewChild('fps', { static: false }) fps: ElementRef;

    constructor() {
        super();
    }

    fps_change (evento) {
       // this.video.playbackRate = AppVideoControlFpsComponent.Round(evento.target.value / this.parent.fps, 2);
       this.video.playbackRate = AppVideoControlFpsComponent.Round(evento.target.value, 2);
    }

    static Round (Number, DecimalPlaces) {
        return Math.round(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    }

    ngAfterViewInit () {

        let opts = Array.prototype.slice.call(this.fps.nativeElement.options);
        let options = opts.filter(o => o.value === this.parent.fps.toString());

        if (options.length) {
            options[0].selected = true;
        }

    }


}
