import {Component} from '@angular/core';
import {AppVideoControlComponent} from "./app-video-control";

@Component({
    selector: 'app-video-control-fast-play',
    template: ''
})

export class AppVideoControlFastPlayComponent extends AppVideoControlComponent{

    static interval = null;
    static timeout = 100;
    static direzione = 0;

    constructor() {
        super()
    }

    public fast_play (direzione) {

        this.video.pause();
        if (AppVideoControlFastPlayComponent.interval) {

            if( direzione !== AppVideoControlFastPlayComponent.direzione) {
                AppVideoControlFastPlayComponent.direzione = direzione;
                AppVideoControlFastPlayComponent._stop();
            } else {
                AppVideoControlFastPlayComponent.direzione = direzione;
                AppVideoControlFastPlayComponent._stop();
                return
            }


        }

        AppVideoControlFastPlayComponent.direzione = direzione;

        AppVideoControlFastPlayComponent.interval = setInterval( () => {
            if (this.video.seeking) return;
            this.video.currentTime += direzione * .1;
        }, AppVideoControlFastPlayComponent.timeout)

    }

    private static _stop () {
        clearInterval(AppVideoControlFastPlayComponent.interval);
        AppVideoControlFastPlayComponent.interval = null;
    }

    onplay () {
        AppVideoControlFastPlayComponent._stop();
    }

    onbegin () {
        AppVideoControlFastPlayComponent._stop();
    }

    onended () {
        AppVideoControlFastPlayComponent._stop();
    }
}