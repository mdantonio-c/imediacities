import {Component, Input, ViewChild, ElementRef, OnChanges} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-time-markers',
    templateUrl: 'app-video-control-time-markers.html'
})

export class AppVideoControlTimeMarkersComponent extends AppVideoControlComponent implements OnChanges{

    @ViewChild('smtpe_mark') smtpe_mark;
    float_mark = '0000.0000';
    frame_mark = '00000';

    interval = null;
    timeout = 100;

    hours:any = '00';
    minutes:any = '00';
    seconds:any = '00';
    smtpe:any = '00';

    constructor() {
        super();
    }

    private static _floor (Number, DecimalPlaces) {
        return Math.floor(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    }

    private _format (time, fps,  smtpe = true) {

        if (time < 0) {
            time = 0;
        }
        this.hours = this._pad(AppVideoControlTimeMarkersComponent._floor((time / 3600), 0) % 24, 2);
        this.minutes = this._pad(AppVideoControlTimeMarkersComponent._floor((time / 60), 0) % 60, 2);
        this.seconds = this._pad(AppVideoControlTimeMarkersComponent._floor((time % 60), 0),2);
        this.smtpe = this._pad(AppVideoControlTimeMarkersComponent._floor((((time % 1) * fps).toFixed(3)), 0),2);

        // const hours = AppVideoControlTimeMarkersComponent._floor((time / 3600), 0) % 24;
        // const minutes = AppVideoControlTimeMarkersComponent._floor((time / 60), 0) % 60;
        // const seconds = AppVideoControlTimeMarkersComponent._floor((time % 60), 0);
        // const frames = AppVideoControlTimeMarkersComponent._floor((((time % 1) * fps).toFixed(3)), 0);
        //return `<strong>&nbsp;&nbsp;${(hours < 10 ? "0" + hours : hours)}</strong>:<strong>${(minutes < 10 ? "0" + minutes : minutes)}</strong>:<strong>${(seconds < 10 ? "0" + seconds : seconds)}</strong>${(smtpe  ? " f <strong>" + (frames < 10 ? "0" + frames : frames) + '</strong>' : '')}`;
    }

    private static _float_time (time) {
        return (Math.round(parseFloat(time) * Math.pow(10, 10)) / Math.pow(10, 10)).toFixed(4);
    }

    public markers_update () {
        this._format(this.video.currentTime, this.parent.fps);
        this.float_mark = this._pad(AppVideoControlTimeMarkersComponent._float_time(this.video.currentTime), 9);
        this.frame_mark = this._pad(this.parent.frame_current(), 5);
    }
    private _pad (Number, Length) {
        let str = ''+ Number;
        while (str.length < Length) {
            str = '0' + str;
        }
        return str;
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

    public onbegin () {

    }

    public onended () {

    }

}