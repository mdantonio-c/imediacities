import {Injectable} from '@angular/core';
import {ApiService} from '/rapydo/src/app/api.service';

@Injectable()
export class AppVideoService {

    private _video = null;

    constructor (private api: ApiService) {

    }

    get (video_id, cb) {

        if (!cb || typeof cb !== 'function') {
            console.log("AppShotService", "Callback mancante");
            return
        }

        this.api.get(
            'videos',
            video_id
        ).subscribe(
            response => {
                console.log("VideoService",  response.data[0]);
                this._video = response.data[0];
                cb(this._video);
            },
            err => {
                alert('ops');
                console.log("err", err);
            }
        );

    }

    video () {
        return this._video;
    }
}