import {Component, Input, ViewChild, ElementRef,} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-time-markers',
    templateUrl: 'app-video-control-time-markers.html'
})

export class AppVideoControlTimeMarkersComponent extends AppVideoControlComponent{

    @ViewChild('smtpe_mark') smtpe_mark;
    @ViewChild('float_mark') float_mark;
    @Input() fps = 24;

    interval = null;
    timeout = 100;

    constructor() {
        super();
    }

    private static _floor (Number, DecimalPlaces) {
        return Math.floor(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    }

    private static _format (time, fps,  smtpe = true) {
        const hours = AppVideoControlTimeMarkersComponent._floor((time / 3600), 0) % 24;
        const minutes = AppVideoControlTimeMarkersComponent._floor((time / 60), 0) % 60;
        const seconds = AppVideoControlTimeMarkersComponent._floor((time % 60), 0);
        const frames = AppVideoControlTimeMarkersComponent._floor((((time % 1) * fps).toFixed(3)), 0);
        return `<strong>${(hours < 10 ? "0" + hours : hours)}</strong>:
                <strong>${(minutes < 10 ? "0" + minutes : minutes)}</strong>:
                <strong>${(seconds < 10 ? "0" + seconds : seconds)}</strong>
                ${(smtpe  ? " f <strong>" + (frames < 10 ? "0" + frames : frames) + '</strong>' : '')}`;
    }

    private static _float_time (time) {
        return (Math.round(parseFloat(time) * Math.pow(10, 10)) / Math.pow(10, 10)).toFixed(4);
    }

    public markers_update () {
        if (this.smtpe_mark) {
            this.smtpe_mark.nativeElement.innerHTML = AppVideoControlTimeMarkersComponent._format(this.video.currentTime, this.fps);
        }
        if (this.float_mark) {
            this.float_mark.nativeElement.innerHTML = AppVideoControlTimeMarkersComponent._float_time(this.video.currentTime);
        }
    }

    public onplay () {
        this.interval = setInterval(() => {
            if (this.video.paused) return;
            this.markers_update()
        }, this.timeout)
    }

    public onpause () {
        clearInterval(this.interval);
    }

    public ontimeupdate () {
        this.markers_update();
    }

}