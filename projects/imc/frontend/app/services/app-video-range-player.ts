import {Injectable} from '@angular/core';

@Injectable()
export class AppVideoRangePlayer {

    private _video;
    private _range = {
        active: false,
        loop: false,
        start: null,
        end: null,
        limit: 0,
        interval: null,
        timer: 100,
        check: function (currentTime) {
            return this.active && this.end && (currentTime >= this.end - this.limit);
        }
    };

    constructor () { };

    public set (conf) {

        this._video = conf.video;

        //  todo 24 sono gli fps
        this._range.start = 1/24 * conf.start;
        this._range.end = 1/24 * conf.end;
        this._range.loop = conf.loop || true;
        this._range.active = true;

        if (this._range.interval) {
            this._unset();
        }

        this._video.currentTime = this._range.start;
        // this._video.play();

        this._range.interval = setInterval(()=>{

            if (!this._video.paused && this._range.check(this._video.currentTime)) {

                this._video.pause();

                if (this._range.loop === false) {
                    this._range.active = false;
                }

                this._video.currentTime = this._range.end;
                this._unset();

            }

        }, this._range.timer);
    }

    public is_active () {
        return this._range.active;
    }

    public get () {
        return this._range;
    }

    private _unset () {

        clearInterval(this._range.interval);
        this._range.interval = null;
    }

}