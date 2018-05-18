import {Injectable} from '@angular/core';

@Injectable()
export class AppVideoControlsFastPlayService {

    public interval = null;
    private timeout = 100;
    public direzione = 0;

    constructor() {
    }

    public fast_play (direzione, video) {

        video.pause();

        if (this.interval) {

            if (direzione !== this.direzione) {
                this.direzione = direzione;
                this.stop();
            } else {
                this.direzione = direzione;
                this.stop();
                return 0;
            }

        }

        this.direzione = direzione;

        this.interval = setInterval(()=>{
            if (video.seeking) return;
            video.currentTime += direzione * .1;
        }, this.timeout);
        return direzione;

    }

    public stop() {
        clearInterval(this.interval);
        this.interval = null;
    }

}